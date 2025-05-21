#!/usr/bin/env python3
"""
CVInsight: Optimized Resume Parsing System

This script provides efficient resume parsing with parallel processing and enhanced error handling,
outputting a single CSV file with the parsed results.
"""
import os
import glob
import pandas as pd
import time
import logging
import concurrent.futures
from tqdm import tqdm
from cvinsight import CVInsightClient
import argparse

# Import our custom plugins
from cvinsight.custom_plugins import (
    RelevantYoEExtractorPlugin,
    EducationStatsExtractorPlugin, 
    WorkStatsExtractorPlugin,
    SocialExtractorPlugin
)

from dotenv import load_dotenv  # For loading environment variables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("Results/cvinsight.log"),
        logging.StreamHandler()
    ]
)

# Create Results directory if it doesn't exist
os.makedirs("Results", exist_ok=True)
print("Ensuring Results directory exists")

# Initialize the client and plugins
def initialize_client():
    load_dotenv()
    # Get API key from environment
    openai_api_key = os.environ.get("OPEN_AI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPEN_AI_API_KEY is not set in the .env file")

    # Initialize the CVInsight client with OpenAI API key
    client = CVInsightClient(
        api_key=openai_api_key,
        provider="openai",
        model_name="o4-mini-2025-04-16"
    )

    # Register custom plugins
    relevant_yoe_plugin = RelevantYoEExtractorPlugin(llm_service=client._llm_service)
    education_stats_plugin = EducationStatsExtractorPlugin(llm_service=client._llm_service)
    work_stats_plugin = WorkStatsExtractorPlugin(llm_service=client._llm_service)
    social_plugin = SocialExtractorPlugin(llm_service=client._llm_service)

    # Add plugins to the plugin manager
    client._plugin_manager.plugins["relevant_yoe_extractor"] = relevant_yoe_plugin
    client._plugin_manager.plugins["education_stats_extractor"] = education_stats_plugin
    client._plugin_manager.plugins["work_stats_extractor"] = work_stats_plugin
    client._plugin_manager.plugins["social_extractor"] = social_plugin

    # Also add to extractors dictionary
    client._plugin_manager.extractors["relevant_yoe_extractor"] = relevant_yoe_plugin
    client._plugin_manager.extractors["education_stats_extractor"] = education_stats_plugin
    client._plugin_manager.extractors["work_stats_extractor"] = work_stats_plugin
    client._plugin_manager.extractors["social_extractor"] = social_plugin

    return client

# Extract data with parallel plugin execution
def extract_with_optimized_plugins(client, path):
    """
    Extract data from a resume path with parallel plugin execution for improved performance.
    Uses a phased approach to respect dependencies while maximizing parallelism.
    """
    start_time = time.time()
    
    # Extract text from the file
    from cvinsight.core.utils.file_utils import read_file
    extracted_text = read_file(path)
    
    # Phase 1: Extract base plugins in parallel
    logging.info("Phase 1: Extracting base information in parallel")
    phase1_start = time.time()
    base_results = {}
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit independent extractions in parallel
            future_profile = executor.submit(client._plugin_manager.extractors['profile_extractor'].extract, extracted_text)
            future_skills = executor.submit(client._plugin_manager.extractors['skills_extractor'].extract, extracted_text)
            future_education = executor.submit(client._plugin_manager.extractors['education_extractor'].extract, extracted_text)
            future_experience = executor.submit(client._plugin_manager.extractors['experience_extractor'].extract, extracted_text)
            future_social = executor.submit(client._plugin_manager.extractors['social_extractor'].extract, extracted_text)
            
            # Track futures
            futures = {
                'profile_result': future_profile,
                'skills_result': future_skills,
                'education_result': future_education,
                'experience_result': future_experience,
                'social_result': future_social
            }
            
            # Wait for all futures to complete with error handling
            for result_key, future in futures.items():
                try:
                    if result_key.endswith('_result'):
                        result, _ = future.result(timeout=60)
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
    
    # Phase 2: Extract plugins that depend on phase 1 results
    logging.info("Phase 2: Extracting dependent information")
    phase2_start = time.time()
    yoe_result = {}
    education_stats_result = {}
    work_stats_result = {}
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
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
            
            futures = {
                'yoe_result': future_yoe,
                'education_stats_result': future_education_stats,
                'work_stats_result': future_work_stats
            }
            
            for result_key, future in futures.items():
                try:
                    result, _ = future.result(timeout=60)
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
    
    # Phase 3: Extract plugins that depend on phase 2 results
    logging.info("Phase 3: Extracting final information")
    phase3_start = time.time()
    relevant_yoe_result = {}
    
    try:
        relevant_yoe_result, _ = client._plugin_manager.extractors['relevant_yoe_extractor'].extract(
            extracted_text, education_stats_result
        )
    except Exception as e:
        logging.error(f"Error in Phase 3 for relevant YoE extraction: {str(e)}")
    
    # Build the resume object
    result = {
        'name': base_results['profile_result'].get('name', ''),
        'contact_number': base_results['profile_result'].get('contact_number', ''),
        'email': base_results['profile_result'].get('email', ''),
        'skills': base_results['skills_result'].get('skills', []),
        'educations': base_results['education_result'].get('educations', []),
        'work_experiences': base_results['experience_result'].get('work_experiences', []),
        'YoE': yoe_result.get('YoE', ''),
        'file_name': os.path.basename(path),
        'plugin_data': {
            'relevant_yoe_extractor': relevant_yoe_result,
            'education_stats_extractor': education_stats_result,
            'work_stats_extractor': work_stats_result,
            'social_extractor': base_results['social_result']
        },
        'processing_time': round(time.time() - start_time, 2)
    }
    
    return result

def main():
    # Initialize client
    client = initialize_client()
    print("\nClient initialized with plugins")
    
    # Collect all resume file paths
    all_file_paths = (
        glob.glob("Resumes/*.pdf")
        + glob.glob("Resumes/*.doc")
        + glob.glob("Resumes/*.docx")
    )
    print(f"Found {len(all_file_paths)} resume files in total.")

    # Process command line arguments
    parser = argparse.ArgumentParser(description='Optimized CVInsight Resume Parser')
    parser.add_argument('--limit', type=int, default=25, help='Number of resumes to process (default: 5)')
    parser.add_argument('--all', action='store_true', help='Process all resumes')
    args = parser.parse_args()

    # Determine how many files to process
    if args.all:
        file_paths = sorted(all_file_paths)
        print(f"Processing all {len(file_paths)} resume files")
    else:
        file_paths = sorted(all_file_paths)[:args.limit]
        print(f"Processing {len(file_paths)} resume files (use --all to process all files)")

    # Print the filenames that will be processed
    print("\nFiles to be processed:")
    for path in file_paths:
        print(f"- {os.path.basename(path)}")

    # Define the names of custom plugins
    custom_plugin_names = [
        "relevant_yoe_extractor",
        "education_stats_extractor",
        "work_stats_extractor",
        "social_extractor",
    ]

    # Process the resumes
    data_list = []
    total_time_start = time.time()
    
    for path in tqdm(file_paths, desc="Parsing resumes"):
        current_row_data = {}
        try:
            filename = os.path.basename(path)
            print(f"\nProcessing: {filename}")
            resume_start_time = time.time()

            # Extract data
            extraction_result = extract_with_optimized_plugins(client, path)
            
            resume_time = time.time() - resume_start_time
            print(f"Resume processing completed in {resume_time:.2f} seconds")
            
            # Process plugin data
            plugin_data = extraction_result.get('plugin_data', {})
            if plugin_data:
                for plugin_key in custom_plugin_names:
                    if plugin_key in plugin_data:
                        plugin_value = plugin_data[plugin_key]
                        if isinstance(plugin_value, dict):
                            for sub_key, sub_value in plugin_value.items():
                                current_row_data[f"{plugin_key}_{sub_key}"] = sub_value
                        else:
                            current_row_data[plugin_key] = plugin_value

            # Process the rest of the extraction result
            if isinstance(extraction_result, dict):
                for key, value in extraction_result.items():
                    if key != 'plugin_data' and key not in custom_plugin_names:
                        current_row_data[key] = value

            # Add file info and status
            current_row_data["filename"] = filename
            current_row_data["parsing_status"] = "success"
            current_row_data["processing_time"] = extraction_result.get('processing_time', resume_time)

            # Remove empty plugin_data key if it exists
            if "plugin_data" in current_row_data and not current_row_data["plugin_data"]:
                del current_row_data["plugin_data"]

            # Add to results
            data_list.append(current_row_data)
            print(f"Successfully parsed: {filename}")
                
        except Exception as e:
            logging.error(f"Error processing {path}: {str(e)}")
            current_row_data = {
                "filename": os.path.basename(path),
                "parsing_status": "failed",
                "error": str(e)
            }
            data_list.append(current_row_data)

    # Calculate processing time
    total_time = time.time() - total_time_start
    print(f"\nTotal processing time: {total_time:.2f} seconds")
    print(f"Average time per resume: {total_time/len(file_paths):.2f} seconds")

    # Create DataFrame and save to CSV
    resume_df = pd.DataFrame(data_list)
    print("\nParsing Summary:")
    print(f"Total files: {len(file_paths)}")
    print(f"Successfully parsed: {(resume_df['parsing_status'] == 'success').sum()}")
    print(f"Failed: {(resume_df['parsing_status'] == 'failed').sum()}")

    # Save to CSV (only output file)
    resume_df.to_csv("Results/resume_analysis_results.csv", index=False)
    print(f"\nResults saved to Results/resume_analysis_results.csv")
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()
