"""
CVInsight Utility Module for Jupyter Notebooks

This module provides easy-to-use functions for parsing resumes in Jupyter notebooks.
It's designed to be imported into another project and used directly.
"""
import os
import glob
import pandas as pd
import time
import logging
import concurrent.futures
from tqdm import tqdm
from cvinsight import CVInsightClient
from typing import List, Dict, Union, Optional, Any
from datetime import datetime
from datetime import datetime

# Import custom plugins
from cvinsight.custom_plugins import (
    RelevantYoEExtractorPlugin,
    EducationStatsExtractorPlugin, 
    WorkStatsExtractorPlugin,
    SocialExtractorPlugin
)

def initialize_client(api_key: str, provider: str = "openai", model_name: str = "o4-mini-2025-04-16") -> CVInsightClient:
    """
    Initialize the CVInsight client with the provided API key and register all custom plugins.
    
    Args:
        api_key: The API key for the LLM provider
        provider: The LLM provider ("openai" or "gemini")
        model_name: The model name to use
        
    Returns:
        An initialized CVInsightClient instance with all plugins registered
    """
    # Initialize the client
    client = CVInsightClient(
        api_key=api_key,
        provider=provider,
        model_name=model_name
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

def parse_single_resume(client: CVInsightClient, resume_path: str, 
                    date_of_resume_submission: str = None, 
                    job_description: str = None) -> Dict[str, Any]:
    """
    Parse a single resume and return the extracted information.
    
    Args:
        client: The initialized CVInsightClient
        resume_path: Path to the resume file
        date_of_resume_submission: Date when the resume was submitted (to calculate duration for 'present' entries)
        job_description: Job description to determine relevance of experience and education
        
    Returns:
        A dictionary containing all extracted resume information
    """
    try:
        # Extract text from the file
        from cvinsight.core.utils.file_utils import read_file
        extracted_text = read_file(resume_path)
        
        # Use the optimized plugin execution approach
        extraction_result = extract_with_optimized_plugins(
            client, 
            resume_path, 
            date_of_resume_submission, 
            job_description
        )
        
        # Flatten plugin data for easier use
        current_row_data = {}
        
        # Process plugin_data
        plugin_data = extraction_result.get('plugin_data', {})
        custom_plugin_names = [
            "relevant_yoe_extractor",
            "education_stats_extractor",
            "work_stats_extractor",
            "social_extractor",
        ]
        
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

        # Add filename
        current_row_data["filename"] = os.path.basename(resume_path)
        current_row_data["parsing_status"] = "success"
        
        # Remove empty plugin_data key if it exists
        if "plugin_data" in current_row_data and not current_row_data["plugin_data"]:
            del current_row_data["plugin_data"]
            
        return current_row_data
        
    except Exception as e:
        # Return error information
        return {
            "filename": os.path.basename(resume_path),
            "parsing_status": "failed",
            "error": str(e)
        }

def parse_many_resumes(client: CVInsightClient, resume_paths: List[str],
                   date_of_resume_submission: str = None,
                   job_description: str = None,
                   use_tqdm: bool = True, 
                   parallel: bool = False, 
                   max_workers: int = 4) -> pd.DataFrame:
    """
    Parse multiple resumes and return a DataFrame with all extracted information.
    
    Args:
        client: The initialized CVInsightClient
        resume_paths: List of paths to resume files
        date_of_resume_submission: Date when the resume was submitted (to calculate duration for 'present' entries)
        job_description: Job description to determine relevance of experience and education
        use_tqdm: Whether to show a progress bar
        parallel: Whether to use parallel processing
        max_workers: Maximum number of workers for parallel processing
        
    Returns:
        A pandas DataFrame containing all extracted resume information
    """
    data_list = []
    
    if parallel:
        # Process resumes in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    parse_single_resume, 
                    client, 
                    path, 
                    date_of_resume_submission, 
                    job_description
                ): path for path in resume_paths
            }
            
            if use_tqdm:
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(resume_paths), desc="Parsing resumes"):
                    path = futures[future]
                    try:
                        result = future.result()
                        data_list.append(result)
                    except Exception as e:
                        # Add error entry
                        data_list.append({
                            "filename": os.path.basename(path),
                            "parsing_status": "failed",
                            "error": str(e)
                        })
            else:
                for future in concurrent.futures.as_completed(futures):
                    path = futures[future]
                    try:
                        result = future.result()
                        data_list.append(result)
                    except Exception as e:
                        # Add error entry
                        data_list.append({
                            "filename": os.path.basename(path),
                            "parsing_status": "failed",
                            "error": str(e)
                        })
    else:
        # Process resumes sequentially
        resume_iterator = tqdm(resume_paths, desc="Parsing resumes") if use_tqdm else resume_paths
        
        for path in resume_iterator:
            result = parse_single_resume(client, path, date_of_resume_submission, job_description)
            data_list.append(result)
    
    # Create DataFrame from results
    return pd.DataFrame(data_list)

def extract_with_optimized_plugins(client, path, date_of_resume_submission=None, job_description=None):
    """
    Extract data from a resume path with parallel plugin execution for improved performance.
    Uses a phased approach to respect dependencies while maximizing parallelism.
    
    Args:
        client: The initialized CVInsightClient
        path: Path to the resume file
        date_of_resume_submission: Date when the resume was submitted (for 'present' calculations)
        job_description: Job description to determine relevance
    """
    start_time = time.time()
    
    # Extract text from the file
    from cvinsight.core.utils.file_utils import read_file
    extracted_text = read_file(path)
    
    # Phase 1: Extract base plugins in parallel
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
                    base_results[result_key] = {} if result_key.endswith('_result') else None
    except Exception:
        base_results = {
            'profile_result': {},
            'skills_result': {},
            'education_result': {},
            'experience_result': {},
            'social_result': {}
        }
    
    # Phase 2: Extract plugins that depend on phase 1 results
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
                except Exception:
                    pass
    except Exception:
        pass
    
    # Phase 3: Extract plugins that depend on phase 2 results (including new relevance data)
    relevant_yoe_result = {}
    
    try:
        # Configure the relevant YoE extractor with job description if provided
        if job_description and hasattr(client._plugin_manager.extractors['relevant_yoe_extractor'], 'job_description'):
            client._plugin_manager.extractors['relevant_yoe_extractor'].job_description = job_description
            
        # If date_of_resume_submission is provided, set it in the relevant contexts
        if date_of_resume_submission:
            # For now, we'll just pass it as an additional parameter
            relevant_yoe_result, _ = client._plugin_manager.extractors['relevant_yoe_extractor'].extract(
                extracted_text, 
                education_stats_result, 
                {'date_of_resume_submission': date_of_resume_submission}
            )
        else:
            relevant_yoe_result, _ = client._plugin_manager.extractors['relevant_yoe_extractor'].extract(
                extracted_text, 
                education_stats_result
            )
    except Exception as e:
        logging.error(f"Error in relevant YoE extraction: {str(e)}")
        relevant_yoe_result = {}
    
    # Process experience data with 'present' handling if date_of_resume_submission is provided
    if date_of_resume_submission and base_results.get('experience_result', {}).get('work_experiences'):
        try:
            # Convert date_of_resume_submission to datetime if it's a string
            if isinstance(date_of_resume_submission, str):
                submission_date = datetime.strptime(date_of_resume_submission, "%Y-%m-%d")
            else:
                submission_date = date_of_resume_submission
                
            # Update any 'present' end dates to use the submission date
            for exp in base_results['experience_result'].get('work_experiences', []):
                if exp.get('end_date', '').lower() == 'present':
                    # Set the end_date to the submission date for calculation purposes
                    exp['calculated_end_date'] = submission_date.strftime("%Y-%m-%d")
                    exp['is_present'] = True
        except Exception as e:
            logging.error(f"Error handling 'present' dates: {str(e)}")
    
    # Build the resume object with new YoE categories
    result = {
        'name': base_results['profile_result'].get('name', ''),
        'contact_number': base_results['profile_result'].get('contact_number', ''),
        'email': base_results['profile_result'].get('email', ''),
        'skills': base_results['skills_result'].get('skills', []),
        'educations': base_results['education_result'].get('educations', []),
        'work_experiences': base_results['experience_result'].get('work_experiences', []),
        'YoE': yoe_result.get('YoE', ''),
        
        # Add new YoE categories (with safer conversion)
        'all_work_yoe': yoe_result.get('YoE', ''),  # Default to original YoE
        'all_edu_yoe': education_stats_result.get('education_years', 0),
    }
    
    # Safely handle YoE calculations
    try:
        # Try to convert YoE to float if possible
        yoe_value = yoe_result.get('YoE', 0)
        edu_years = education_stats_result.get('education_years', 0)
        
        # Handle numeric strings - extract first number or use 0
        import re
        def safe_float_convert(value):
            if value is None:
                return 0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Try to extract the first number from the string (e.g., "6 Years 11 Months" -> 6)
                matches = re.findall(r'(\d+)', value)
                if matches:
                    return float(matches[0])
            return 0
            
        yoe_float = safe_float_convert(yoe_value)
        edu_float = safe_float_convert(edu_years)
        
        # Store both the original string value and the numeric approximation
        result['all_work_yoe_numeric'] = yoe_float
        result['all_edu_yoe_numeric'] = edu_float
        result['all_total_yoe'] = yoe_float + edu_float
    except Exception as e:
        # If conversion fails, use string values and set numeric to 0
        logging.warning(f"Error converting YoE values to numeric: {str(e)}")
        result['all_total_yoe'] = f"{result['all_work_yoe']} + {result['all_edu_yoe']} (non-numeric)"
        result['all_work_yoe_numeric'] = 0
        result['all_edu_yoe_numeric'] = 0
    
    # Add relevant YoE fields if available
    result['relevant_work_yoe'] = relevant_yoe_result.get('relevant_job_experience_years', 0)
    result['relevant_edu_yoe'] = relevant_yoe_result.get('relevant_education_years', 0)  
    result['relevant_total_yoe'] = relevant_yoe_result.get('total_relevant_experience_years', 0)
    
    # Add metadata
    result['file_name'] = os.path.basename(path)
    result['date_of_resume_submission'] = date_of_resume_submission
    result['job_description_provided'] = bool(job_description)
    
    # Add plugin data
    result['plugin_data'] = {
        'relevant_yoe_extractor': relevant_yoe_result,
        'education_stats_extractor': education_stats_result,
        'work_stats_extractor': work_stats_result,
        'social_extractor': base_results['social_result']
    }
    
    result['processing_time'] = round(time.time() - start_time, 2)
    
    return result
    
    return result

def find_resumes(directory_path: str) -> List[str]:
    """
    Find all resume files in a directory.
    
    Args:
        directory_path: Path to the directory containing resume files
        
    Returns:
        List of paths to resume files
    """
    return (
        glob.glob(os.path.join(directory_path, "*.pdf")) +
        glob.glob(os.path.join(directory_path, "*.doc")) +
        glob.glob(os.path.join(directory_path, "*.docx"))
    )
