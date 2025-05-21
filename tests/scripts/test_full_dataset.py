#!/usr/bin/env python3
"""
Full Dataset Test Script for CVInsight resume parsing system.

This script runs the CVInsight parser on all available resumes to generate
comprehensive performance metrics and validate the system's improvements.
"""
import os
import sys
import pandas as pd
import time
import logging
import argparse
from tqdm import tqdm
import json
from datetime import datetime

# Add the project root to sys.path when running as a script
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import CVInsight components
from cvinsight import CVInsightClient
from cvinsight.core.utils.file_utils import read_file
from cvinsight.custom_plugins import (
    RelevantYoEExtractorPlugin,
    EducationStatsExtractorPlugin, 
    WorkStatsExtractorPlugin,
    SocialExtractorPlugin
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Results/full_dataset_test.log"),
        logging.StreamHandler()
    ]
)

def run_test(client, resume_paths, output_dir="Results", limit=None, save_intermediate=True):
    """
    Run the full test on a set of resume paths.
    
    Args:
        client: Initialized CVInsightClient
        resume_paths: List of paths to resume files
        output_dir: Directory to save results
        limit: Optional limit on number of resumes to process
        save_intermediate: Whether to save intermediate results
        
    Returns:
        DataFrame with results and detailed metrics
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Limit the number of files if specified
    if limit and limit > 0:
        resume_paths = resume_paths[:limit]
    
    # Add timestamp to result filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(output_dir, f"full_test_results_{timestamp}.csv")
    metrics_file = os.path.join(output_dir, f"full_test_metrics_{timestamp}.json")
    
    # Store test data and metrics
    data_list = []
    metrics = {
        "total_files": len(resume_paths),
        "processed_files": 0,
        "successful_files": 0,
        "failed_files": 0,
        "total_processing_time": 0,
        "individual_times": [],
        "phase_times": {
            "phase1_times": [],
            "phase2_times": [],
            "phase3_times": []
        },
        "errors": [],
        "start_time": datetime.now().isoformat(),
        "end_time": None
    }
    
    # Define custom plugin names for data collection
    custom_plugin_names = [
        "relevant_yoe_extractor",
        "education_stats_extractor",
        "work_stats_extractor",
        "social_extractor",
    ]
    
    # Process each resume
    total_time_start = time.time()
    
    for path in tqdm(resume_paths, desc="Processing resumes"):
        current_row_data = {}  # Holds all data for the current row
        file_start_time = time.time()
        
        try:
            filename = os.path.basename(path)
            logging.info(f"Processing: {filename}")
            
            # Extract text from the file
            extracted_text = read_file(path)
            
            # Extract information with detailed phase timing
            phase_results, phase_timings = extract_with_phase_timing(client, extracted_text)
            
            # Store the plugin_data separately if it exists
            plugin_data = phase_results.get('plugin_data', {})
            if plugin_data:
                # Add each custom plugin's data to the current row
                for plugin_key in custom_plugin_names:
                    if plugin_key in plugin_data:
                        plugin_value = plugin_data[plugin_key]
                        if isinstance(plugin_value, dict):
                            # This is a custom plugin with dictionary output, flatten it
                            for sub_key, sub_value in plugin_value.items():
                                current_row_data[f"{plugin_key}_{sub_key}"] = sub_value
                        else:
                            # This is a custom plugin with non-dict output
                            current_row_data[plugin_key] = plugin_value
            
            # Process the rest of the extraction result
            if isinstance(phase_results, dict):
                # Add all the top-level data that isn't from our custom plugins
                for key, value in phase_results.items():
                    if key != 'plugin_data' and key not in custom_plugin_names:
                        current_row_data[key] = value
            
            # Add filename, status, and processing times
            file_time = time.time() - file_start_time
            current_row_data["filename"] = filename
            current_row_data["parsing_status"] = "success"
            current_row_data["processing_time"] = file_time
            current_row_data["phase1_time"] = phase_timings.get('phase1', 0)
            current_row_data["phase2_time"] = phase_timings.get('phase2', 0)
            current_row_data["phase3_time"] = phase_timings.get('phase3', 0)
            
            # Update metrics
            metrics["processed_files"] += 1
            metrics["successful_files"] += 1
            metrics["individual_times"].append(file_time)
            metrics["phase_times"]["phase1_times"].append(phase_timings.get('phase1', 0))
            metrics["phase_times"]["phase2_times"].append(phase_timings.get('phase2', 0))
            metrics["phase_times"]["phase3_times"].append(phase_timings.get('phase3', 0))
            
            logging.info(f"Successfully parsed {filename} in {file_time:.2f} seconds")
            
        except Exception as e:
            file_time = time.time() - file_start_time
            error_message = f"Error parsing {os.path.basename(path)}: {str(e)}"
            logging.error(error_message)
            
            # Add a minimal entry to keep track of failed files
            current_row_data = {
                "filename": os.path.basename(path),
                "parsing_status": "failed",
                "error": str(e),
                "processing_time": file_time
            }
            
            # Update metrics
            metrics["processed_files"] += 1
            metrics["failed_files"] += 1
            metrics["individual_times"].append(file_time)
            metrics["errors"].append({
                "filename": os.path.basename(path),
                "error": str(e),
                "time": file_time
            })
        
        # Add to results
        data_list.append(current_row_data)
        
        # Save intermediate results if enabled
        if save_intermediate and len(data_list) % 5 == 0:
            temp_df = pd.DataFrame(data_list)
            temp_df.to_csv(os.path.join(output_dir, "intermediate_results.csv"), index=False)
            logging.info(f"Saved intermediate results after processing {len(data_list)} files")
    
    # Calculate total processing time
    total_time = time.time() - total_time_start
    metrics["total_processing_time"] = total_time
    metrics["average_time_per_resume"] = total_time / len(resume_paths) if resume_paths else 0
    metrics["end_time"] = datetime.now().isoformat()
    
    # Create DataFrame from results
    results_df = pd.DataFrame(data_list)
    
    # Calculate and add aggregate metrics
    if 'processing_time' in results_df.columns:
        metrics["min_processing_time"] = results_df['processing_time'].min() if not results_df.empty else 0
        metrics["max_processing_time"] = results_df['processing_time'].max() if not results_df.empty else 0
        metrics["median_processing_time"] = results_df['processing_time'].median() if not results_df.empty else 0
        
        successful_times = results_df.loc[results_df['parsing_status'] == 'success', 'processing_time']
        metrics["avg_successful_time"] = successful_times.mean() if not successful_times.empty else 0
    
    # Calculate average phase times
    for phase in ['phase1_time', 'phase2_time', 'phase3_time']:
        if phase in results_df.columns:
            metrics[f"avg_{phase}"] = results_df[phase].mean() if not results_df.empty else 0
    
    # Save final results
    results_df.to_csv(results_file, index=False)
    
    # Save metrics to JSON
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logging.info(f"Full test completed. Results saved to {results_file}")
    logging.info(f"Test metrics saved to {metrics_file}")
    
    return results_df, metrics

def extract_with_phase_timing(client, extracted_text):
    """
    Extract data from text with detailed phase timing.
    
    Args:
        client: Initialized CVInsightClient
        extracted_text: Extracted text content from a resume
        
    Returns:
        Tuple of (extraction_results, phase_timings)
    """
    result = {}
    phase_timings = {}
    
    # Phase 1: Extract base plugins in parallel
    phase1_start = time.time()
    base_results = {}
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all the independent extractions in parallel
            future_profile = executor.submit(client._plugin_manager.extractors['profile_extractor'].extract, extracted_text)
            future_skills = executor.submit(client._plugin_manager.extractors['skills_extractor'].extract, extracted_text)
            future_education = executor.submit(client._plugin_manager.extractors['education_extractor'].extract, extracted_text)
            future_experience = executor.submit(client._plugin_manager.extractors['experience_extractor'].extract, extracted_text)
            future_social = executor.submit(client._plugin_manager.extractors['social_extractor'].extract, extracted_text)
            
            # Create a dictionary to track futures
            futures = {
                'profile_result': future_profile,
                'skills_result': future_skills,
                'education_result': future_education,
                'experience_result': future_experience,
                'social_result': future_social
            }
            
            # Wait for all futures to complete, with error handling
            for result_key, future in futures.items():
                try:
                    if result_key.endswith('_result'):
                        # First element is the actual result, second is token usage
                        result, _ = future.result(timeout=60)  # Add a timeout to avoid hanging
                        base_results[result_key] = result
                    else:
                        base_results[result_key] = future.result(timeout=60)
                except Exception as e:
                    logging.error(f"Error in Phase 1 for {result_key}: {str(e)}")
                    base_results[result_key] = {} if result_key.endswith('_result') else None
    except Exception as e:
        logging.error(f"Error in Phase 1 parallel processing: {str(e)}")
        base_results = {
            'profile_result': {},
            'skills_result': {},
            'education_result': {},
            'experience_result': {},
            'social_result': {}
        }
    
    phase1_time = time.time() - phase1_start
    phase_timings['phase1'] = phase1_time
    
    # Phase 2: Extract plugins that depend on phase 1 results
    phase2_start = time.time()
    yoe_result = {}
    education_stats_result = {}
    work_stats_result = {}
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # These can be done in parallel as they depend on different inputs
            future_yoe = executor.submit(
                client._plugin_manager.extractors['yoe_extractor'].extract, 
                base_results.get('experience_result', {})
            )
            future_education_stats = executor.submit(
                client._plugin_manager.extractors['education_stats_extractor'].extract, 
                base_results.get('education_result', {})
            )
            future_work_stats = executor.submit(
                client._plugin_manager.extractors['work_stats_extractor'].extract, 
                base_results.get('experience_result', {})
            )
            
            # Create a dictionary to track futures
            futures = {
                'yoe_result': future_yoe,
                'education_stats_result': future_education_stats,
                'work_stats_result': future_work_stats
            }
            
            # Wait for all futures to complete, with error handling
            for result_key, future in futures.items():
                try:
                    # First element is the actual result, second is token usage
                    result, _ = future.result(timeout=60)  # Add a timeout to avoid hanging
                    if result_key == 'yoe_result':
                        yoe_result = result
                    elif result_key == 'education_stats_result':
                        education_stats_result = result
                    elif result_key == 'work_stats_result':
                        work_stats_result = result
                except Exception as e:
                    logging.error(f"Error in Phase 2 for {result_key}: {str(e)}")
    except Exception as e:
        logging.error(f"Error in Phase 2 parallel processing: {str(e)}")
    
    phase2_time = time.time() - phase2_start
    phase_timings['phase2'] = phase2_time
    
    # Phase 3: Extract plugins that depend on phase 2 results
    phase3_start = time.time()
    relevant_yoe_result = {}
    
    try:
        relevant_yoe_result, _ = client._plugin_manager.extractors['relevant_yoe_extractor'].extract(
            extracted_text, education_stats_result
        )
    except Exception as e:
        logging.error(f"Error in Phase 3 for relevant YoE extraction: {str(e)}")
    
    phase3_time = time.time() - phase3_start
    phase_timings['phase3'] = phase3_time
    
    # Build the resume object
    result = {
        'name': base_results.get('profile_result', {}).get('name', ''),
        'contact_number': base_results.get('profile_result', {}).get('contact_number', ''),
        'email': base_results.get('profile_result', {}).get('email', ''),
        'skills': base_results.get('skills_result', {}).get('skills', []),
        'educations': base_results.get('education_result', {}).get('educations', []),
        'work_experiences': base_results.get('experience_result', {}).get('work_experiences', []),
        'YoE': yoe_result.get('YoE', ''),
        'plugin_data': {
            'relevant_yoe_extractor': relevant_yoe_result,
            'education_stats_extractor': education_stats_result,
            'work_stats_extractor': work_stats_result,
            'social_extractor': base_results.get('social_result', {})
        }
    }
    
    return result, phase_timings

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='CVInsight Full Dataset Test')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of resumes to process')
    parser.add_argument('--model', type=str, default="o4-mini-2025-04-16", help='Model to use (default: o4-mini-2025-04-16)')
    parser.add_argument('--output', type=str, default="Results", help='Output directory (default: Results)')
    args = parser.parse_args()
    
    # Load environment variables for API keys
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get API key from environment
    openai_api_key = os.environ.get("OPEN_AI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPEN_AI_API_KEY is not set in the .env file")
    
    # Initialize client
    client = CVInsightClient(
        api_key=openai_api_key,
        provider="openai",
        model_name=args.model
    )
    
    # Register custom plugins
    relevant_yoe_plugin = RelevantYoEExtractorPlugin(llm_service=client._llm_service)
    education_stats_plugin = EducationStatsExtractorPlugin(llm_service=client._llm_service)
    work_stats_plugin = WorkStatsExtractorPlugin(llm_service=client._llm_service)
    social_plugin = SocialExtractorPlugin(llm_service=client._llm_service)
    
    # Add plugins directly to the plugin manager's plugins dictionary
    client._plugin_manager.plugins["relevant_yoe_extractor"] = relevant_yoe_plugin
    client._plugin_manager.plugins["education_stats_extractor"] = education_stats_plugin
    client._plugin_manager.plugins["work_stats_extractor"] = work_stats_plugin
    client._plugin_manager.plugins["social_extractor"] = social_plugin
    
    # Also add to extractors dictionary since they are ExtractorPlugins
    client._plugin_manager.extractors["relevant_yoe_extractor"] = relevant_yoe_plugin
    client._plugin_manager.extractors["education_stats_extractor"] = education_stats_plugin
    client._plugin_manager.extractors["work_stats_extractor"] = work_stats_plugin
    client._plugin_manager.extractors["social_extractor"] = social_plugin
    
    # Collect all resume file paths
    all_file_paths = (
        glob.glob("Resumes/*.pdf")
        + glob.glob("Resumes/*.doc")
        + glob.glob("Resumes/*.docx")
    )
    print(f"Found {len(all_file_paths)} resume files")
    
    if args.limit:
        print(f"Limiting to {args.limit} files")
    
    # Run the test
    results_df, metrics = run_test(
        client=client,
        resume_paths=sorted(all_file_paths),
        output_dir=args.output,
        limit=args.limit
    )
    
    # Print summary
    print("\nTest Completed:")
    print(f"- Total files processed: {metrics['processed_files']}")
    print(f"- Successfully parsed: {metrics['successful_files']}")
    print(f"- Failed: {metrics['failed_files']}")
    print(f"- Total processing time: {metrics['total_processing_time']:.2f} seconds")
    print(f"- Average time per resume: {metrics['average_time_per_resume']:.2f} seconds")
    
    # Also run the performance analysis
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from analyze_performance import analyze_performance
        
        # Find the latest results file
        latest_results = sorted(
            [f for f in os.listdir(args.output) if f.startswith("full_test_results_")],
            reverse=True
        )
        
        if latest_results:
            results_path = os.path.join(args.output, latest_results[0])
            print(f"\nRunning performance analysis on {results_path}")
            analyze_performance(results_path)
        else:
            print("\nNo results file found for performance analysis")
    except Exception as e:
        print(f"Error running performance analysis: {str(e)}")

if __name__ == "__main__":
    # Import additional required modules
    import concurrent.futures
    import glob
    main()
