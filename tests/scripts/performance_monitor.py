#!/usr/bin/env python3
"""
Performance Monitor for CVInsight

This script analyzes the performance data from CVInsight runs and
generates detailed metrics and visualizations.

Usage:
    python performance_monitor.py [--input FILE] [--output DIR]

Options:
    --input FILE    Results CSV file to analyze (default: Results/resume_analysis_results.csv)
    --output DIR    Directory to store outputs (default: Results/performance)
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import json
from datetime import datetime

# Configure argument parser
parser = argparse.ArgumentParser(description='CVInsight Performance Monitor')
parser.add_argument('--input', type=str, default='Results/resume_analysis_results.csv',
                    help='Results CSV file to analyze')
parser.add_argument('--output', type=str, default='Results/performance',
                    help='Directory to store outputs')
args = parser.parse_args()

# Ensure output directory exists
os.makedirs(args.output, exist_ok=True)

# Load results data
try:
    df = pd.read_csv(args.input)
    print(f"Loaded {len(df)} records from {args.input}")
except Exception as e:
    print(f"Error loading data: {str(e)}")
    sys.exit(1)

# Generate timestamp for output files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create performance metrics dictionary
metrics = {
    "analysis_timestamp": timestamp,
    "total_records": len(df),
    "successful_records": int((df['parsing_status'] == 'success').sum()),
    "failed_records": int((df['parsing_status'] == 'failed').sum()),
    "success_rate": float((df['parsing_status'] == 'success').sum() / len(df) * 100),
}

# Calculate processing time statistics
if 'processing_time' in df.columns:
    successful_df = df[df['parsing_status'] == 'success']
    metrics["processing_time"] = {
        "mean": float(successful_df['processing_time'].mean()),
        "median": float(successful_df['processing_time'].median()),
        "min": float(successful_df['processing_time'].min()),
        "max": float(successful_df['processing_time'].max()),
        "std": float(successful_df['processing_time'].std()),
        "total": float(successful_df['processing_time'].sum()),
    }
    
    # Generate a histogram of processing times
    plt.figure(figsize=(10, 6))
    plt.hist(successful_df['processing_time'], bins=20, alpha=0.7, color='cornflowerblue')
    plt.xlabel('Processing Time (seconds)')
    plt.ylabel('Number of Resumes')
    plt.title('Resume Processing Time Distribution')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Add mean and median lines
    mean_time = successful_df['processing_time'].mean()
    median_time = successful_df['processing_time'].median()
    plt.axvline(mean_time, color='r', linestyle='--', label=f'Mean: {mean_time:.2f}s')
    plt.axvline(median_time, color='g', linestyle=':', label=f'Median: {median_time:.2f}s')
    plt.legend()
    
    # Save the figure
    plt.savefig(os.path.join(args.output, f"processing_time_histogram_{timestamp}.png"))
    print(f"Saved processing time histogram to {args.output}/processing_time_histogram_{timestamp}.png")

# Calculate custom plugin metrics
custom_plugin_columns = [col for col in df.columns 
                         if col.startswith(('relevant_yoe_extractor_', 
                                            'education_stats_extractor_',
                                            'work_stats_extractor_',
                                            'social_extractor_'))]

if custom_plugin_columns:
    metrics["custom_plugins"] = {
        "total_columns": len(custom_plugin_columns),
        "columns": custom_plugin_columns
    }
    
    # Extract more detailed stats about specific values
    if 'relevant_yoe_extractor_relevant_education_years' in df.columns:
        ed_years = df['relevant_yoe_extractor_relevant_education_years'].dropna()
        if not ed_years.empty:
            metrics["education_years"] = {
                "mean": float(ed_years.mean()),
                "median": float(ed_years.median()),
                "min": float(ed_years.min()),
                "max": float(ed_years.max()),
            }
    
    if 'relevant_yoe_extractor_relevant_job_experience_years' in df.columns:
        job_years = df['relevant_yoe_extractor_relevant_job_experience_years'].dropna()
        if not job_years.empty:
            metrics["job_experience_years"] = {
                "mean": float(job_years.mean()),
                "median": float(job_years.median()),
                "min": float(job_years.min()),
                "max": float(job_years.max()),
            }

    # Generate a comparison plot between education and job experience
    if ('relevant_yoe_extractor_relevant_education_years' in df.columns and
        'relevant_yoe_extractor_relevant_job_experience_years' in df.columns):
        
        # Filter to only successful records and drop NAs
        plot_df = df[df['parsing_status'] == 'success'].dropna(subset=[
            'relevant_yoe_extractor_relevant_education_years',
            'relevant_yoe_extractor_relevant_job_experience_years'
        ])
        
        if not plot_df.empty:
            plt.figure(figsize=(10, 6))
            
            # Create a scatter plot
            plt.scatter(
                plot_df['relevant_yoe_extractor_relevant_education_years'],
                plot_df['relevant_yoe_extractor_relevant_job_experience_years'],
                alpha=0.7, 
                c='cornflowerblue',
                s=80
            )
            
            plt.xlabel('Education Years')
            plt.ylabel('Job Experience Years')
            plt.title('Education vs. Job Experience Years')
            plt.grid(True, alpha=0.3)
            
            # Add a trend line
            if len(plot_df) > 1:
                z = np.polyfit(
                    plot_df['relevant_yoe_extractor_relevant_education_years'],
                    plot_df['relevant_yoe_extractor_relevant_job_experience_years'],
                    1
                )
                p = np.poly1d(z)
                x_range = np.linspace(
                    plot_df['relevant_yoe_extractor_relevant_education_years'].min(),
                    plot_df['relevant_yoe_extractor_relevant_education_years'].max(),
                    100
                )
                plt.plot(x_range, p(x_range), 'r--', alpha=0.8)
            
            plt.tight_layout()
            plt.savefig(os.path.join(args.output, f"education_vs_job_experience_{timestamp}.png"))
            print(f"Saved education vs. job experience plot to {args.output}/education_vs_job_experience_{timestamp}.png")

# Save metrics to JSON file
metrics_file = os.path.join(args.output, f"performance_metrics_{timestamp}.json")
with open(metrics_file, 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"Saved performance metrics to {metrics_file}")

# Generate a summary report in markdown format
report_lines = [
    "# CVInsight Performance Analysis Report",
    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "",
    "## Performance Summary",
    f"- Total records analyzed: {metrics['total_records']}",
    f"- Successfully processed: {metrics['successful_records']} ({metrics['success_rate']:.2f}%)",
    f"- Failed: {metrics['failed_records']}",
    "",
]

if 'processing_time' in metrics:
    pt = metrics['processing_time']
    report_lines.extend([
        "## Processing Time Statistics",
        f"- Mean processing time: {pt['mean']:.2f} seconds",
        f"- Median processing time: {pt['median']:.2f} seconds",
        f"- Minimum: {pt['min']:.2f} seconds",
        f"- Maximum: {pt['max']:.2f} seconds",
        f"- Standard deviation: {pt['std']:.2f} seconds",
        f"- Total processing time: {pt['total']:.2f} seconds",
        "",
    ])

if 'education_years' in metrics:
    ed = metrics['education_years']
    report_lines.extend([
        "## Education Years",
        f"- Mean: {ed['mean']:.2f} years",
        f"- Median: {ed['median']:.2f} years",
        f"- Range: {ed['min']:.1f} to {ed['max']:.1f} years",
        "",
    ])

if 'job_experience_years' in metrics:
    job = metrics['job_experience_years']
    report_lines.extend([
        "## Job Experience Years",
        f"- Mean: {job['mean']:.2f} years",
        f"- Median: {job['median']:.2f} years",
        f"- Range: {job['min']:.1f} to {job['max']:.1f} years",
        "",
    ])

report_lines.extend([
    "## Generated Visualizations",
    f"- Processing time histogram: processing_time_histogram_{timestamp}.png",
])

if 'education_years' in metrics and 'job_experience_years' in metrics:
    report_lines.append(f"- Education vs. job experience: education_vs_job_experience_{timestamp}.png")

report_file = os.path.join(args.output, f"performance_report_{timestamp}.md")
with open(report_file, 'w') as f:
    f.write('\n'.join(report_lines))
print(f"Generated performance report at {report_file}")

print("\nPerformance analysis complete!")
