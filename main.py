from utils.logging_utils import setup_logging
from resume_processor import ResumeProcessor
import config
import logging
import os
import sys
import argparse
import json

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Resume Analysis Tool")
    parser.add_argument('--resume', type=str, help='Process a single resume file and show token usage report')
    parser.add_argument('--report-only', action='store_true', help='Only show token usage report for existing processed resume')
    parser.add_argument('--log-dir', type=str, default='./logs/token_usage', help='Directory to store token usage logs')
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    # Create a resume processor using config directories
    processor = ResumeProcessor(
        resume_dir=config.RESUME_DIR,
        output_dir=config.OUTPUT_DIR,
        log_dir=args.log_dir
    )
    
    # Process a single resume if specified
    if args.resume:
        resume_path = args.resume
        if not os.path.exists(resume_path):
            # Try with resume dir prefix
            resume_path = os.path.join(config.RESUME_DIR, args.resume)
            if not os.path.exists(resume_path):
                logging.error(f"Resume file not found: {args.resume}")
                sys.exit(1)
        
        if args.report_only:
            # Try to load the processed resume from the results directory
            resume_basename = os.path.basename(resume_path)
            resume_name = os.path.splitext(resume_basename)[0]
            result_path = os.path.join(config.OUTPUT_DIR, f"{resume_name}.json")
            
            if os.path.exists(result_path):
                with open(result_path, 'r') as f:
                    resume_data = json.load(f)
                
                # Create a Resume object from the loaded data
                from models import Resume
                resume = Resume.model_validate(resume_data)
                resume.file_name = resume_basename
                
                # Find the most recent token usage log for this resume
                log_files = []
                if os.path.exists(args.log_dir):
                    log_files = [f for f in os.listdir(args.log_dir) 
                                if f.startswith(f"{resume_name}_token_usage_") and f.endswith(".json")]
                
                # Sort by timestamp in filename (newest first)
                log_files.sort(reverse=True)
                
                if log_files:
                    # Load the most recent token usage data
                    log_file_path = os.path.join(args.log_dir, log_files[0])
                    with open(log_file_path, 'r') as f:
                        token_data = json.load(f)
                        resume.token_usage = token_data.get("token_usage", {})
                    
                    # Print token usage report
                    processor.print_token_usage_report(resume, log_file_path)
                else:
                    logging.warning(f"No token usage logs found for {resume_basename}")
                    processor.print_token_usage_report(resume)
            else:
                logging.error(f"Processed resume not found: {result_path}")
                sys.exit(1)
        else:
            # Process the resume and show token usage report
            logging.info(f"Processing single resume: {resume_path}")
            resume = processor.process_resume(resume_path)
            
            if resume:
                processor.save_resume(resume)
                logging.info(f"Resume processing complete")
            else:
                logging.error(f"Failed to process resume: {resume_path}")
                sys.exit(1)
    else:
        # Process all resumes
        processed_count, error_count = processor.process_all_resumes()
        
        # Log summary
        logging.info(f"Resume processing complete. Processed: {processed_count}, Errors: {error_count}")

if __name__ == "__main__":
    main()
