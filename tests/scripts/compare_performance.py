#!/usr/bin/env python3
"""
Performance Comparison Script for CVInsight

This script compares two different runs of the CVInsight system to measure improvements.
It generates detailed visualizations and statistics to highlight the differences.

Usage:
    python compare_performance.py --baseline FILE --current FILE [--output DIR]

Options:
    --baseline FILE    Baseline results CSV file to compare against
    --current FILE     Current results CSV file to analyze
    --output DIR       Directory to store outputs (default: Results/comparisons)
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
parser = argparse.ArgumentParser(description='CVInsight Performance Comparison')
parser.add_argument('--baseline', type=str, required=True,
                    help='Baseline results CSV file to compare against')
parser.add_argument('--current', type=str, required=True,
                    help='Current results CSV file to analyze')
parser.add_argument('--output', type=str, default='Results/comparisons',
                    help='Directory to store outputs')
args = parser.parse_args()

# Ensure output directory exists
os.makedirs(args.output, exist_ok=True)

# Load baseline and current data
try:
    baseline_df = pd.read_csv(args.baseline)
    current_df = pd.read_csv(args.current)
    print(f"Loaded baseline: {len(baseline_df)} records from {args.baseline}")
    print(f"Loaded current: {len(current_df)} records from {args.current}")
except Exception as e:
    print(f"Error loading data: {str(e)}")
    sys.exit(1)

# Generate timestamp for output files
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create comparison metrics dictionary
metrics = {
    "comparison_timestamp": timestamp,
    "baseline": {
        "file": args.baseline,
        "total_records": len(baseline_df),
        "successful_records": int((baseline_df['parsing_status'] == 'success').sum()),
        "success_rate": float((baseline_df['parsing_status'] == 'success').sum() / len(baseline_df) * 100),
    },
    "current": {
        "file": args.current,
        "total_records": len(current_df),
        "successful_records": int((current_df['parsing_status'] == 'success').sum()),
        "success_rate": float((current_df['parsing_status'] == 'success').sum() / len(current_df) * 100),
    },
}

# Calculate improvement percentages
metrics["improvements"] = {
    "success_rate": metrics["current"]["success_rate"] - metrics["baseline"]["success_rate"],
}

# Compare processing times
if 'processing_time' in baseline_df.columns and 'processing_time' in current_df.columns:
    baseline_success = baseline_df[baseline_df['parsing_status'] == 'success']
    current_success = current_df[current_df['parsing_status'] == 'success']
    
    metrics["baseline"]["processing_time"] = {
        "mean": float(baseline_success['processing_time'].mean()),
        "median": float(baseline_success['processing_time'].median()),
        "min": float(baseline_success['processing_time'].min()),
        "max": float(baseline_success['processing_time'].max()),
    }
    
    metrics["current"]["processing_time"] = {
        "mean": float(current_success['processing_time'].mean()),
        "median": float(current_success['processing_time'].median()),
        "min": float(current_success['processing_time'].min()),
        "max": float(current_success['processing_time'].max()),
    }
    
    baseline_mean = metrics["baseline"]["processing_time"]["mean"]
    current_mean = metrics["current"]["processing_time"]["mean"]
    
    # Calculate processing time improvement
    time_diff = baseline_mean - current_mean
    percent_improvement = (time_diff / baseline_mean) * 100 if baseline_mean > 0 else 0
    
    metrics["improvements"]["processing_time"] = {
        "time_difference": time_diff,
        "percent_improvement": percent_improvement,
    }
    
    # Create a bar chart comparing processing times
    plt.figure(figsize=(12, 7))
    
    # Define the metrics to show
    metrics_labels = ['Mean', 'Median', 'Min', 'Max']
    baseline_values = [
        metrics["baseline"]["processing_time"]["mean"],
        metrics["baseline"]["processing_time"]["median"],
        metrics["baseline"]["processing_time"]["min"],
        metrics["baseline"]["processing_time"]["max"],
    ]
    
    current_values = [
        metrics["current"]["processing_time"]["mean"],
        metrics["current"]["processing_time"]["median"],
        metrics["current"]["processing_time"]["min"],
        metrics["current"]["processing_time"]["max"],
    ]
    
    # Set up the bar chart
    x = np.arange(len(metrics_labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 7))
    rects1 = ax.bar(x - width/2, baseline_values, width, label='Baseline', color='#ff9999', alpha=0.8)
    rects2 = ax.bar(x + width/2, current_values, width, label='Current', color='#66b3ff', alpha=0.8)
    
    # Add labels and title
    ax.set_ylabel('Processing Time (seconds)')
    ax.set_title('Processing Time Comparison: Baseline vs. Current')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_labels)
    ax.legend()
    
    # Add value labels on top of each bar
    def add_labels(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    add_labels(rects1)
    add_labels(rects2)
    
    # Add a text box with improvement percentage
    if percent_improvement > 0:
        improvement_text = f"Improvement: {percent_improvement:.2f}%"
        ax.text(0.02, 0.95, improvement_text, transform=ax.transAxes, 
                bbox=dict(facecolor='green', alpha=0.2), fontsize=12)
    elif percent_improvement < 0:
        worsening_text = f"Worsening: {abs(percent_improvement):.2f}%"
        ax.text(0.02, 0.95, worsening_text, transform=ax.transAxes, 
                bbox=dict(facecolor='red', alpha=0.2), fontsize=12)
    
    fig.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(args.output, f"processing_time_comparison_{timestamp}.png"))
    print(f"Saved processing time comparison to {args.output}/processing_time_comparison_{timestamp}.png")

# Compare distribution of processing times with histograms
if 'processing_time' in baseline_df.columns and 'processing_time' in current_df.columns:
    baseline_success = baseline_df[baseline_df['parsing_status'] == 'success']
    current_success = current_df[current_df['parsing_status'] == 'success']
    
    plt.figure(figsize=(12, 7))
    
    # Create overlapping histograms
    plt.hist(baseline_success['processing_time'], bins=20, alpha=0.5, label='Baseline', color='#ff9999')
    plt.hist(current_success['processing_time'], bins=20, alpha=0.5, label='Current', color='#66b3ff')
    
    # Add mean lines
    plt.axvline(baseline_success['processing_time'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Baseline Mean: {baseline_success["processing_time"].mean():.2f}s')
    plt.axvline(current_success['processing_time'].mean(), color='blue', linestyle='--', 
                linewidth=2, label=f'Current Mean: {current_success["processing_time"].mean():.2f}s')
    
    plt.xlabel('Processing Time (seconds)')
    plt.ylabel('Number of Resumes')
    plt.title('Processing Time Distribution Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(args.output, f"processing_time_distribution_comparison_{timestamp}.png"))
    print(f"Saved processing time distribution comparison to {args.output}/processing_time_distribution_comparison_{timestamp}.png")

# Save metrics to JSON file
metrics_file = os.path.join(args.output, f"comparison_metrics_{timestamp}.json")
with open(metrics_file, 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"Saved comparison metrics to {metrics_file}")

# Generate a summary report in markdown format
report_lines = [
    "# CVInsight Performance Comparison Report",
    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "",
    "## Comparison Summary",
    f"- Baseline file: {metrics['baseline']['file']}",
    f"- Current file: {metrics['current']['file']}",
    "",
    "## Success Rate Comparison",
    f"- Baseline success rate: {metrics['baseline']['success_rate']:.2f}%",
    f"- Current success rate: {metrics['current']['success_rate']:.2f}%",
    f"- Improvement: {metrics['improvements']['success_rate']:.2f}%",
    "",
]

if 'processing_time' in metrics["baseline"] and 'processing_time' in metrics["current"]:
    baseline_pt = metrics["baseline"]["processing_time"]
    current_pt = metrics["current"]["processing_time"]
    improvement = metrics["improvements"]["processing_time"]
    
    report_lines.extend([
        "## Processing Time Comparison",
        "### Baseline",
        f"- Mean processing time: {baseline_pt['mean']:.2f} seconds",
        f"- Median processing time: {baseline_pt['median']:.2f} seconds",
        f"- Range: {baseline_pt['min']:.2f} to {baseline_pt['max']:.2f} seconds",
        "",
        "### Current",
        f"- Mean processing time: {current_pt['mean']:.2f} seconds",
        f"- Median processing time: {current_pt['median']:.2f} seconds",
        f"- Range: {current_pt['min']:.2f} to {current_pt['max']:.2f} seconds",
        "",
        "### Improvement",
        f"- Time difference: {improvement['time_difference']:.2f} seconds",
        f"- Percentage improvement: {improvement['percent_improvement']:.2f}%",
        "",
    ])

report_lines.extend([
    "## Generated Visualizations",
    f"- Processing time comparison: processing_time_comparison_{timestamp}.png",
    f"- Processing time distribution comparison: processing_time_distribution_comparison_{timestamp}.png",
])

report_file = os.path.join(args.output, f"comparison_report_{timestamp}.md")
with open(report_file, 'w') as f:
    f.write('\n'.join(report_lines))
print(f"Generated comparison report at {report_file}")

print("\nPerformance comparison complete!")
