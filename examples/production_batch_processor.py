#!/usr/bin/env python3
"""
CVInsight Production Batch Processor

A production-ready script for batch processing resumes using CVInsight.
This script demonstrates how to integrate CVInsight from external repositories
with enterprise-grade features including logging, error handling, and reporting.

Usage:
    python production_batch_processor.py --resume-dir /path/to/resumes --job-desc "Job description here"
    python production_batch_processor.py --config config.json

Features:
- Command-line interface with comprehensive options
- Production-grade logging and error handling
- Performance metrics and detailed reporting
- Multiple output formats (CSV, JSON)
- Parallel processing with configurable workers
- Resume discovery and validation
- Integration examples for external repositories

Author: CVInsight Team
Version: 1.0.0
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

# Add CVInsight to path for external repository integration
CVINSIGHT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if CVINSIGHT_PATH not in sys.path:
    sys.path.insert(0, CVINSIGHT_PATH)

try:
    from cvinsight.notebook_utils import (
        initialize_client,
        parse_many_resumes,
        find_resumes
    )
except ImportError as e:
    print(f"Error importing CVInsight: {e}")
    print("Please ensure CVInsight is properly installed or the path is correct.")
    sys.exit(1)


class ProductionBatchProcessor:
    """Production-ready batch processor for CVInsight resume analysis."""
    
    def __init__(self, config: Dict):
        """Initialize the batch processor with configuration."""
        self.config = config
        self.logger = self._setup_logging()
        self.client = None
        self.results = []
        self.metrics = {
            'start_time': None,
            'end_time': None,
            'total_resumes': 0,
            'successful_parses': 0,
            'failed_parses': 0,
            'processing_time': 0,
            'avg_time_per_resume': 0
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup production logging with file and console handlers."""
        logger = logging.getLogger('CVInsight_BatchProcessor')
        logger.setLevel(getattr(logging, self.config.get('log_level', 'INFO')))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler for detailed logs
        if self.config.get('log_file'):
            os.makedirs(os.path.dirname(self.config['log_file']), exist_ok=True)
            file_handler = logging.FileHandler(self.config['log_file'])
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        
        # Console handler for user feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.get('console_log_level', 'INFO')))
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def initialize_cvinsight(self) -> bool:
        """Initialize CVInsight client with error handling."""
        try:
            self.logger.info("Initializing CVInsight client...")
            
            api_key = self.config.get('api_key') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found in config or environment")
            
            self.client = initialize_client(
                api_key=api_key,
                provider=self.config.get('provider', 'openai'),
                model_name=self.config.get('model_name', 'gpt-4o-mini')
            )
            
            self.logger.info("CVInsight client initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CVInsight client: {e}")
            return False
    
    def discover_resumes(self, resume_dir: str) -> List[str]:
        """Discover and validate resume files in the specified directory."""
        try:
            self.logger.info(f"Discovering resumes in: {resume_dir}")
            
            if not os.path.exists(resume_dir):
                raise FileNotFoundError(f"Resume directory not found: {resume_dir}")
            
            resume_paths = find_resumes(resume_dir)
            
            if not resume_paths:
                self.logger.warning(f"No resume files found in: {resume_dir}")
                return []
            
            # Apply limit if specified
            limit = self.config.get('resume_limit')
            if limit and limit > 0:
                resume_paths = resume_paths[:limit]
                self.logger.info(f"Limited to first {limit} resumes")
            
            self.logger.info(f"Found {len(resume_paths)} resume(s) to process")
            return resume_paths
            
        except Exception as e:
            self.logger.error(f"Error discovering resumes: {e}")
            return []
    
    def process_batch(self, resume_paths: List[str], job_description: str) -> bool:
        """Process a batch of resumes with comprehensive error handling."""
        try:
            self.metrics['start_time'] = time.time()
            self.metrics['total_resumes'] = len(resume_paths)
            
            self.logger.info(f"Starting batch processing of {len(resume_paths)} resumes")
            self.logger.info(f"Job description preview: {job_description[:100]}...")
            
            # Process resumes
            results_df = parse_many_resumes(
                client=self.client,
                resume_paths=resume_paths,
                date_of_resume_submission=datetime.now().strftime("%Y-%m-%d"),
                job_description=job_description,
                use_tqdm=True,
                parallel=self.config.get('parallel', True),
                max_workers=self.config.get('max_workers', 4)
            )
            
            self.metrics['end_time'] = time.time()
            self.metrics['processing_time'] = self.metrics['end_time'] - self.metrics['start_time']
            
            # Analyze results
            if results_df is not None and not results_df.empty:
                self._analyze_results(results_df)
                self.results = results_df
                return True
            else:
                self.logger.error("No results returned from batch processing")
                return False
                
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return False
    
    def _analyze_results(self, results_df: pd.DataFrame) -> None:
        """Analyze processing results and update metrics."""
        total_resumes = len(results_df)
        successful_parses = len(results_df[results_df['parsing_status'] == 'success'])
        failed_parses = total_resumes - successful_parses
        
        self.metrics.update({
            'successful_parses': successful_parses,
            'failed_parses': failed_parses,
            'success_rate': (successful_parses / total_resumes) * 100 if total_resumes > 0 else 0,
            'avg_time_per_resume': self.metrics['processing_time'] / total_resumes if total_resumes > 0 else 0
        })
        
        self.logger.info(f"Processing completed: {successful_parses}/{total_resumes} successful")
        self.logger.info(f"Success rate: {self.metrics['success_rate']:.1f}%")
        self.logger.info(f"Total processing time: {self.metrics['processing_time']:.2f} seconds")
        self.logger.info(f"Average time per resume: {self.metrics['avg_time_per_resume']:.2f} seconds")
        
        # Log top candidates if successful parses exist
        if successful_parses > 0:
            successful_df = results_df[results_df['parsing_status'] == 'success']
            if 'overall_match_score' in successful_df.columns:
                top_candidates = successful_df.nlargest(3, 'overall_match_score')[
                    ['name', 'overall_match_score', 'resume_path']
                ]
                self.logger.info("Top 3 candidates:")
                for _, candidate in top_candidates.iterrows():
                    self.logger.info(f"  - {candidate['name']}: {candidate['overall_match_score']}/100")
    
    def save_results(self) -> bool:
        """Save results in multiple formats with comprehensive error handling."""
        if not hasattr(self, 'results') or self.results is None or self.results.empty:
            self.logger.warning("No results to save")
            return False
        
        try:
            output_dir = self.config.get('output_dir', './Results')
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"batch_results_{timestamp}"
            
            # Save CSV
            if self.config.get('save_csv', True):
                csv_path = os.path.join(output_dir, f"{base_filename}.csv")
                self.results.to_csv(csv_path, index=False)
                self.logger.info(f"Results saved to CSV: {csv_path}")
            
            # Save JSON
            if self.config.get('save_json', True):
                json_path = os.path.join(output_dir, f"{base_filename}.json")
                self.results.to_json(json_path, orient='records', indent=2)
                self.logger.info(f"Results saved to JSON: {json_path}")
            
            # Save metrics
            metrics_path = os.path.join(output_dir, f"metrics_{timestamp}.json")
            with open(metrics_path, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
            self.logger.info(f"Metrics saved to: {metrics_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            return False
    
    def generate_report(self) -> str:
        """Generate a comprehensive processing report."""
        if not hasattr(self, 'results') or self.results is None:
            return "No processing results available for report generation."
        
        report_lines = [
            "=" * 60,
            "CVInsight Production Batch Processing Report",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Processing Summary:",
            f"  Total Resumes: {self.metrics['total_resumes']}",
            f"  Successful Parses: {self.metrics['successful_parses']}",
            f"  Failed Parses: {self.metrics['failed_parses']}",
            f"  Success Rate: {self.metrics.get('success_rate', 0):.1f}%",
            "",
            "Performance Metrics:",
            f"  Total Processing Time: {self.metrics['processing_time']:.2f} seconds",
            f"  Average Time per Resume: {self.metrics['avg_time_per_resume']:.2f} seconds",
            "",
            "Configuration:",
            f"  Parallel Processing: {self.config.get('parallel', True)}",
            f"  Max Workers: {self.config.get('max_workers', 4)}",
            f"  Model: {self.config.get('model_name', 'gpt-4o-mini')}",
            ""
        ]
        
        # Add top candidates if available
        if not self.results.empty and 'overall_match_score' in self.results.columns:
            successful_df = self.results[self.results['parsing_status'] == 'success']
            if not successful_df.empty:
                top_candidates = successful_df.nlargest(5, 'overall_match_score')
                report_lines.extend([
                    "Top 5 Candidates:",
                    "-" * 20
                ])
                for i, (_, candidate) in enumerate(top_candidates.iterrows(), 1):
                    name = candidate.get('name', 'Unknown')
                    score = candidate.get('overall_match_score', 0)
                    report_lines.append(f"  {i}. {name}: {score}/100")
                report_lines.append("")
        
        # Add error summary if any failures
        if self.metrics['failed_parses'] > 0:
            failed_df = self.results[self.results['parsing_status'] != 'success']
            report_lines.extend([
                "Failed Parses Summary:",
                "-" * 20
            ])
            for _, failed in failed_df.iterrows():
                resume_name = os.path.basename(failed.get('resume_path', 'Unknown'))
                error = failed.get('error_message', 'Unknown error')
                report_lines.append(f"  • {resume_name}: {error}")
            report_lines.append("")
        
        report_lines.extend([
            "Integration Example:",
            "-" * 20,
            "This script demonstrates how to integrate CVInsight into",
            "external projects with production-grade features.",
            "",
            "Key integration patterns used:",
            "  • Environment-based configuration",
            "  • Comprehensive error handling",
            "  • Structured logging and metrics",
            "  • Multiple output formats",
            "  • Parallel processing optimization",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    def run(self, resume_dir: str, job_description: str) -> bool:
        """Main execution method for the batch processor."""
        self.logger.info("Starting CVInsight Production Batch Processor")
        
        # Initialize CVInsight
        if not self.initialize_cvinsight():
            return False
        
        # Discover resumes
        resume_paths = self.discover_resumes(resume_dir)
        if not resume_paths:
            return False
        
        # Process batch
        if not self.process_batch(resume_paths, job_description):
            return False
        
        # Save results
        if not self.save_results():
            self.logger.warning("Failed to save results, but processing completed")
        
        # Generate and display report
        report = self.generate_report()
        print("\n" + report)
        
        self.logger.info("Batch processing completed successfully")
        return True


def load_config_file(config_path: str) -> Dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)


def create_sample_config() -> Dict:
    """Create a sample configuration dictionary."""
    return {
        "api_key": "",  # Will use OPENAI_API_KEY environment variable if empty
        "provider": "openai",
        "model_name": "gpt-4o-mini",
        "parallel": True,
        "max_workers": 4,
        "resume_limit": 0,  # 0 means no limit
        "log_level": "INFO",
        "console_log_level": "INFO",
        "log_file": "./logs/batch_processor.log",
        "output_dir": "./Results",
        "save_csv": True,
        "save_json": True
    }


def main():
    """Main entry point for the production batch processor."""
    parser = argparse.ArgumentParser(
        description="CVInsight Production Batch Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python production_batch_processor.py --resume-dir ./resumes --job-desc "Software Engineer with Python experience"
  python production_batch_processor.py --config config.json
  python production_batch_processor.py --resume-dir ./resumes --job-desc-file job.txt --parallel --workers 8
  python production_batch_processor.py --create-config
        """
    )
    
    # Configuration options
    parser.add_argument('--config', type=str, help='Path to JSON configuration file')
    parser.add_argument('--create-config', action='store_true', 
                       help='Create a sample configuration file and exit')
    
    # Resume processing options
    parser.add_argument('--resume-dir', type=str, help='Directory containing resumes to process')
    parser.add_argument('--job-desc', type=str, help='Job description text')
    parser.add_argument('--job-desc-file', type=str, help='File containing job description')
    
    # Processing options
    parser.add_argument('--parallel', action='store_true', help='Enable parallel processing')
    parser.add_argument('--no-parallel', action='store_true', help='Disable parallel processing')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
    parser.add_argument('--limit', type=int, help='Limit number of resumes to process')
    
    # Output options
    parser.add_argument('--output-dir', type=str, default='./Results', 
                       help='Output directory for results')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    
    # Model options
    parser.add_argument('--model', type=str, default='gpt-4o-mini', help='LLM model to use')
    parser.add_argument('--provider', type=str, default='openai', help='LLM provider')
    
    args = parser.parse_args()
    
    # Handle create-config option
    if args.create_config:
        config = create_sample_config()
        config_path = 'batch_processor_config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Sample configuration created: {config_path}")
        print("Edit the configuration file and run with: --config batch_processor_config.json")
        return
    
    # Load or create configuration
    if args.config:
        config = load_config_file(args.config)
    else:
        config = create_sample_config()
    
    # Override config with command line arguments
    if args.resume_dir:
        # Command line mode - validate required arguments
        if not args.job_desc and not args.job_desc_file:
            parser.error("Either --job-desc or --job-desc-file is required when using --resume-dir")
        
        # Load job description
        if args.job_desc_file:
            try:
                with open(args.job_desc_file, 'r') as f:
                    job_description = f.read().strip()
            except Exception as e:
                print(f"Error reading job description file: {e}")
                sys.exit(1)
        else:
            job_description = args.job_desc
        
        # Override config with command line args
        config.update({
            'parallel': args.parallel if args.parallel else not args.no_parallel,
            'max_workers': args.workers,
            'resume_limit': args.limit or 0,
            'log_level': args.log_level,
            'output_dir': args.output_dir,
            'model_name': args.model,
            'provider': args.provider
        })
        
        # Initialize and run processor
        processor = ProductionBatchProcessor(config)
        success = processor.run(args.resume_dir, job_description)
        sys.exit(0 if success else 1)
    
    else:
        # Config file mode - validate config has required fields
        if 'resume_dir' not in config or 'job_description' not in config:
            parser.error("Configuration file must contain 'resume_dir' and 'job_description' fields")
        
        processor = ProductionBatchProcessor(config)
        success = processor.run(config['resume_dir'], config['job_description'])
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()