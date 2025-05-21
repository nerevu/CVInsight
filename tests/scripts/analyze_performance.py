#!/usr/bin/env python3
"""
Performance analysis script for CVInsight resume parsing system.

This script runs the CVInsight parser on the full dataset and generates
detailed performance metrics, comparing them with a baseline if available.
"""
import os
import sys
import pandas as pd
import time
import logging
import argparse
import matplotlib.pyplot as plt
from datetime import datetime

# Add the project root to sys.path when running as a script
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Results/performance_analysis.log"),
        logging.StreamHandler()
    ]
)

def analyze_performance(results_file_path, baseline_file_path=None):
    """
    Analyze performance metrics from results CSV file and compare with baseline if provided.
    
    Args:
        results_file_path: Path to the results CSV file
        baseline_file_path: Optional path to a baseline results file for comparison
    """
    # Create Results directory if it doesn't exist
    os.makedirs("Results/performance", exist_ok=True)
    
    # Load the results data
    try:
        results_df = pd.read_csv(results_file_path)
        logging.info(f"Loaded results from {results_file_path} with {len(results_df)} records")
    except Exception as e:
        logging.error(f"Failed to load results from {results_file_path}: {str(e)}")
        return
    
    # Load baseline data if provided
    baseline_df = None
    if baseline_file_path and os.path.exists(baseline_file_path):
        try:
            baseline_df = pd.read_csv(baseline_file_path)
            logging.info(f"Loaded baseline from {baseline_file_path} with {len(baseline_df)} records")
        except Exception as e:
            logging.error(f"Failed to load baseline from {baseline_file_path}: {str(e)}")
    
    # Calculate performance metrics
    performance_metrics = {}
    
    # Get processing success rate
    success_count = (results_df['parsing_status'] == 'success').sum()
    total_count = len(results_df)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    performance_metrics['success_rate'] = success_rate
    performance_metrics['total_files'] = total_count
    performance_metrics['successful_files'] = success_count
    performance_metrics['failed_files'] = total_count - success_count
    
    # Calculate processing time statistics
    if 'processing_time' in results_df.columns:
        processing_times = results_df.loc[results_df['parsing_status'] == 'success', 'processing_time']
        if not processing_times.empty:
            performance_metrics['avg_processing_time'] = processing_times.mean()
            performance_metrics['min_processing_time'] = processing_times.min()
            performance_metrics['max_processing_time'] = processing_times.max()
            performance_metrics['median_processing_time'] = processing_times.median()
            performance_metrics['total_processing_time'] = processing_times.sum()
    
    # Compare with baseline if available
    improvement_metrics = {}
    if baseline_df is not None and 'processing_time' in baseline_df.columns:
        baseline_times = baseline_df.loc[baseline_df['parsing_status'] == 'success', 'processing_time']
        current_times = results_df.loc[results_df['parsing_status'] == 'success', 'processing_time']
        
        if not baseline_times.empty and not current_times.empty:
            baseline_avg = baseline_times.mean()
            current_avg = current_times.mean()
            
            time_improvement = baseline_avg - current_avg
            percent_improvement = (time_improvement / baseline_avg) * 100 if baseline_avg > 0 else 0
            
            improvement_metrics['baseline_avg_time'] = baseline_avg
            improvement_metrics['current_avg_time'] = current_avg
            improvement_metrics['time_improvement'] = time_improvement
            improvement_metrics['percent_improvement'] = percent_improvement
            
            # Calculate success rate improvement
            baseline_success_rate = (baseline_df['parsing_status'] == 'success').sum() / len(baseline_df) * 100
            current_success_rate = success_rate
            success_rate_improvement = current_success_rate - baseline_success_rate
            
            improvement_metrics['baseline_success_rate'] = baseline_success_rate
            improvement_metrics['current_success_rate'] = current_success_rate
            improvement_metrics['success_rate_improvement'] = success_rate_improvement
    
    # Generate visualizations
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Processing time distribution
    if 'processing_time' in results_df.columns:
        plt.figure(figsize=(10, 6))
        plt.hist(results_df.loc[results_df['parsing_status'] == 'success', 'processing_time'], bins=20, alpha=0.7)
        plt.xlabel('Processing Time (seconds)')
        plt.ylabel('Number of Resumes')
        plt.title('Resume Processing Time Distribution')
        plt.grid(True, alpha=0.3)
        plt.savefig(f"Results/performance/time_distribution_{timestamp}.png")
        plt.close()
    
    # Compare with baseline if available
    if baseline_df is not None and 'processing_time' in baseline_df.columns and 'processing_time' in results_df.columns:
        # Comparison bar chart
        plt.figure(figsize=(12, 6))
        
        # Filter for successful parses only
        baseline_times = baseline_df.loc[baseline_df['parsing_status'] == 'success', 'processing_time']
        current_times = results_df.loc[results_df['parsing_status'] == 'success', 'processing_time']
        
        if not baseline_times.empty and not current_times.empty:
            labels = ['Average', 'Median', 'Maximum']
            baseline_values = [baseline_times.mean(), baseline_times.median(), baseline_times.max()]
            current_values = [current_times.mean(), current_times.median(), current_times.max()]
            
            x = range(len(labels))
            width = 0.35
            
            plt.bar(x, baseline_values, width, label='Baseline', color='#ff9999')
            plt.bar([i + width for i in x], current_values, width, label='Current', color='#66b3ff')
            
            plt.xlabel('Metric')
            plt.ylabel('Processing Time (seconds)')
            plt.title('Performance Comparison: Baseline vs. Current')
            plt.xticks([i + width/2 for i in x], labels)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(f"Results/performance/comparison_{timestamp}.png")
            plt.close()
    
    # Generate summary report
    report_lines = [
        "# CVInsight Performance Analysis Report",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Performance Metrics",
        f"- Total files processed: {performance_metrics.get('total_files', 'N/A')}",
        f"- Successfully parsed: {performance_metrics.get('successful_files', 'N/A')} ({performance_metrics.get('success_rate', 'N/A'):.2f}%)",
        f"- Failed: {performance_metrics.get('failed_files', 'N/A')}",
        "",
        "### Processing Time Statistics",
        f"- Average time per resume: {performance_metrics.get('avg_processing_time', 'N/A'):.2f} seconds",
        f"- Median time per resume: {performance_metrics.get('median_processing_time', 'N/A'):.2f} seconds",
        f"- Minimum time: {performance_metrics.get('min_processing_time', 'N/A'):.2f} seconds",
        f"- Maximum time: {performance_metrics.get('max_processing_time', 'N/A'):.2f} seconds",
        f"- Total processing time: {performance_metrics.get('total_processing_time', 'N/A'):.2f} seconds",
        ""
    ]
    
    if improvement_metrics:
        report_lines.extend([
            "## Performance Improvement",
            f"- Baseline average time: {improvement_metrics.get('baseline_avg_time', 'N/A'):.2f} seconds",
            f"- Current average time: {improvement_metrics.get('current_avg_time', 'N/A'):.2f} seconds",
            f"- Time improvement: {improvement_metrics.get('time_improvement', 'N/A'):.2f} seconds",
            f"- Percentage improvement: {improvement_metrics.get('percent_improvement', 'N/A'):.2f}%",
            "",
            f"- Baseline success rate: {improvement_metrics.get('baseline_success_rate', 'N/A'):.2f}%",
            f"- Current success rate: {improvement_metrics.get('current_success_rate', 'N/A'):.2f}%",
            f"- Success rate improvement: {improvement_metrics.get('success_rate_improvement', 'N/A'):.2f}%",
            ""
        ])
    
    # Add visualization references
    report_lines.extend([
        "## Visualizations",
        "Generated visualizations are available in the Results/performance directory:",
        "",
        f"- Time distribution: Results/performance/time_distribution_{timestamp}.png"
    ])
    
    if baseline_df is not None:
        report_lines.append(f"- Performance comparison: Results/performance/comparison_{timestamp}.png")
    
    # Write report to file
    report_path = f"Results/performance_report_{timestamp}.md"
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))
    
    logging.info(f"Performance analysis report written to {report_path}")
    
    # Also output a CSV with the metrics
    metrics_df = pd.DataFrame({
        **performance_metrics,
        **improvement_metrics
    }, index=[0])
    
    metrics_path = f"Results/performance_metrics_{timestamp}.csv"
    metrics_df.to_csv(metrics_path, index=False)
    logging.info(f"Performance metrics saved to {metrics_path}")
    
    return performance_metrics, improvement_metrics

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='CVInsight Performance Analysis Tool')
    parser.add_argument('--results', type=str, default="Results/resume_analysis_results.csv",
                      help='Path to the results CSV file (default: Results/resume_analysis_results.csv)')
    parser.add_argument('--baseline', type=str, default=None,
                      help='Optional path to a baseline results file for comparison')
    args = parser.parse_args()
    
    # Run the performance analysis
    start_time = time.time()
    performance_metrics, improvement_metrics = analyze_performance(args.results, args.baseline)
    end_time = time.time()
    
    # Print summary
    print("\nPerformance Analysis Summary:")
    print(f"- Total files processed: {performance_metrics.get('total_files', 'N/A')}")
    print(f"- Success rate: {performance_metrics.get('success_rate', 'N/A'):.2f}%")
    print(f"- Average processing time: {performance_metrics.get('avg_processing_time', 'N/A'):.2f} seconds")
    
    if improvement_metrics:
        print("\nPerformance Improvement:")
        print(f"- Time improvement: {improvement_metrics.get('time_improvement', 'N/A'):.2f} seconds ({improvement_metrics.get('percent_improvement', 'N/A'):.2f}%)")
        print(f"- Success rate improvement: {improvement_metrics.get('success_rate_improvement', 'N/A'):.2f}%")
    
    print(f"\nAnalysis completed in {end_time - start_time:.2f} seconds.")
    print("See the generated report for detailed metrics and visualizations.")

if __name__ == "__main__":
    main()
