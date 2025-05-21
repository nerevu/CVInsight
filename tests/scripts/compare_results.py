"""
Utility to compare extraction results between different runs.
"""
import os
import sys
import pandas as pd
import numpy as np

# Add the project root to sys.path when running as a script
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def load_and_compare_results():
    """
    Load and compare the extraction results from different runs.
    """
    # Define the file paths
    main_results_path = os.path.join("Results", "resume_analysis_results.csv")
    optimized_results_path = os.path.join("Results", "resume_custom_plugins_analysis.csv")
    
    # Check if files exist
    if not os.path.exists(main_results_path) or not os.path.exists(optimized_results_path):
        print("Error: Results files not found. Please run both main.py and optimized_main.py first.")
        return
        
    # Load the CSV files into pandas DataFrames
    main_df = pd.read_csv(main_results_path)
    optimized_df = pd.read_csv(optimized_results_path)
    
    print(f"Main results shape: {main_df.shape}")
    print(f"Optimized results shape: {optimized_df.shape}")
    
    # Print column names for debugging
    print("\nMain results columns:")
    print(main_df.columns.tolist())
    print("\nOptimized results columns:")
    print(optimized_df.columns.tolist())
    
    # Make sure the filenames are comparable
    main_df['filename'] = main_df['filename'].str.strip()
    optimized_df['filename'] = optimized_df['filename'].str.strip()
    
    # Find common files
    common_files = set(main_df['filename']) & set(optimized_df['filename'])
    print(f"\nNumber of common files: {len(common_files)}")
    print("Common files:", common_files)
    
    if len(common_files) == 0:
        print("No common files found. Cannot compare results.")
        return
    
    # Filter to only include common files
    main_df = main_df[main_df['filename'].isin(common_files)]
    optimized_df = optimized_df[optimized_df['filename'].isin(common_files)]
    
    # Sort by filename to ensure the same order
    main_df = main_df.sort_values('filename').reset_index(drop=True)
    optimized_df = optimized_df.sort_values('filename').reset_index(drop=True)
    
    # Check for key plugin data columns to compare
    relevant_yoe_cols_main = [col for col in main_df.columns if 'relevant_yoe_extractor' in col]
    relevant_yoe_cols_opt = [col for col in optimized_df.columns if 'relevant_yoe_extractor' in col]
    
    print("\nRelevant YoE columns in main:", relevant_yoe_cols_main)
    print("Relevant YoE columns in optimized:", relevant_yoe_cols_opt)
    
    # Check if we can compare education years
    if 'relevant_yoe_extractor_relevant_education_years' in main_df.columns and 'relevant_yoe_extractor_relevant_education_years' in optimized_df.columns:
        print("\n--- Education Years Comparison ---")
        for filename in common_files:
            main_row = main_df[main_df['filename'] == filename]
            opt_row = optimized_df[optimized_df['filename'] == filename]
            
            if len(main_row) == 0 or len(opt_row) == 0:
                print(f"File: {filename} - Not found in one of the datasets")
                continue
                
            main_ed_years = main_row['relevant_yoe_extractor_relevant_education_years'].values[0]
            opt_ed_years = opt_row['relevant_yoe_extractor_relevant_education_years'].values[0]
            
            print(f"File: {filename}")
            print(f"  Main: {main_ed_years}")
            print(f"  Optimized: {opt_ed_years}")
            if main_ed_years != opt_ed_years:
                print(f"  Difference: {opt_ed_years - main_ed_years}")
            print()
    else:
        print("Education years columns not found in both datasets")
    
    # Check if we can compare total experience
    if 'relevant_yoe_extractor_total_relevant_experience_years' in main_df.columns and 'relevant_yoe_extractor_total_relevant_experience_years' in optimized_df.columns:
        print("\n--- Total Relevant Experience Comparison ---")
        for filename in common_files:
            main_row = main_df[main_df['filename'] == filename]
            opt_row = optimized_df[optimized_df['filename'] == filename]
            
            if len(main_row) == 0 or len(opt_row) == 0:
                print(f"File: {filename} - Not found in one of the datasets")
                continue
                
            main_total = main_row['relevant_yoe_extractor_total_relevant_experience_years'].values[0]
            opt_total = opt_row['relevant_yoe_extractor_total_relevant_experience_years'].values[0]
            
            print(f"File: {filename}")
            print(f"  Main: {main_total}")
            print(f"  Optimized: {opt_total}")
            if main_total != opt_total:
                print(f"  Difference: {opt_total - main_total}")
            print()
    else:
        print("Total relevant experience columns not found in both datasets")
    
    # Check if we can compare degree status
    if all(col in main_df.columns for col in ['education_stats_extractor_highest_degree', 'education_stats_extractor_highest_degree_status']) and \
       all(col in optimized_df.columns for col in ['education_stats_extractor_highest_degree', 'education_stats_extractor_highest_degree_status']):
        print("\n--- Highest Degree Comparison ---")
        for filename in common_files:
            main_row = main_df[main_df['filename'] == filename]
            opt_row = optimized_df[optimized_df['filename'] == filename]
            
            if len(main_row) == 0 or len(opt_row) == 0:
                print(f"File: {filename} - Not found in one of the datasets")
                continue
                
            main_degree = main_row['education_stats_extractor_highest_degree'].values[0]
            main_status = main_row['education_stats_extractor_highest_degree_status'].values[0]
            
            opt_degree = opt_row['education_stats_extractor_highest_degree'].values[0]
            opt_status = opt_row['education_stats_extractor_highest_degree_status'].values[0]
            
            print(f"File: {filename}")
            print(f"  Main: {main_degree} ({main_status})")
            print(f"  Optimized: {opt_degree} ({opt_status})")
            print()
    else:
        print("Highest degree columns not found in both datasets")

if __name__ == "__main__":
    load_and_compare_results()
