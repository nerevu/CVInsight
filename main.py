from utils.logging_utils import setup_logging
from utils.log_utils import cleanup_token_usage_logs
from utils.cleanup import cleanup_pycache
import config
import logging
import os
import sys
import argparse
import json

# Imports for plugin-based system
import llm_service
from base_plugins.plugin_manager import PluginManager
from resume_processor import PluginResumeProcessor

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Resume Analysis Tool")
    parser.add_argument('--resume', type=str, help='Process a single resume file and show token usage report')
    parser.add_argument('--report-only', action='store_true', help='Only show token usage report for existing processed resume')
    parser.add_argument('--log-dir', type=str, default='./logs/token_usage', help='Directory to store token usage logs')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--cleanup', action='store_true', help='Clean up __pycache__ directories and compiled Python files')
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    # Clean up old token usage logs
    cleanup_token_usage_logs(args.log_dir)
    
    # Handle cleanup command
    if args.cleanup:
        logging.info("Running cleanup of __pycache__ directories and compiled Python files")
        dir_count, file_count = cleanup_pycache()
        logging.info(f"Cleanup complete. Removed {dir_count} __pycache__ directories and {file_count} compiled Python files")
        return
    
    # Set log level to DEBUG if verbose mode is enabled
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose logging enabled")
    
    # Log command line arguments
    logging.info(f"Command line arguments: {args}")
    
    # Initialize plugin-based resume processor
    logging.info("Initializing plugin-based resume processor")
    try:
        # Initialize plugin manager
        logging.debug("Creating plugin manager")
        plugin_manager = PluginManager(llm_service)
        
        # Load plugins
        logging.debug("Loading plugins")
        plugins = plugin_manager.load_all_plugins()
        logging.info(f"Loaded {len(plugins)} plugins for resume analysis")
        
        # Create a plugin-based resume processor
        logging.debug("Creating plugin-based resume processor")
        processor = PluginResumeProcessor(
            resume_dir=config.RESUME_DIR,
            output_dir=config.OUTPUT_DIR,
            log_dir=args.log_dir,
            plugin_manager=plugin_manager
        )
        logging.info("Using plugin-based resume processor")
    except Exception as e:
        logging.exception(f"Error initializing plugin system: {e}")
        sys.exit(1)
    
    # Process a single resume if specified
    if args.resume:
        resume_path = args.resume
        if not os.path.exists(resume_path):
            # Try with resume dir prefix
            resume_path = os.path.join(config.RESUME_DIR, args.resume)
            if not os.path.exists(resume_path):
                logging.error(f"Resume file not found: {args.resume}")
                sys.exit(1)
        
        logging.info(f"Resume file: {resume_path}")
        
        if args.report_only:
            # Try to load the processed resume from the results directory
            resume_basename = os.path.basename(resume_path)
            resume_name = os.path.splitext(resume_basename)[0]
            result_path = os.path.join(config.OUTPUT_DIR, f"{resume_name}.json")
            
            logging.info(f"Looking for processed resume at {result_path}")
            
            if os.path.exists(result_path):
                with open(result_path, 'r') as f:
                    resume_data = json.load(f)
                
                # Create a Resume object from the loaded data
                from models.resume_models import Resume
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
            try:
                resume = processor.process_resume(resume_path)
                
                if resume:
                    processor.save_resume(resume)
                    logging.info(f"Resume processing complete")
                    
                    # Print token usage report
                    print("\n===== Token Usage Report =====")
                    print(f"Resume: {os.path.basename(resume_path)}")
                    
                    if resume.token_usage:
                        token_usage = resume.token_usage
                        print(f"\nTotal tokens used: {token_usage.get('total_tokens', 0)}")
                        print(f"Prompt tokens: {token_usage.get('prompt_tokens', 0)}")
                        print(f"Completion tokens: {token_usage.get('completion_tokens', 0)}")
                        
                        # If we have detailed breakdown by extractor
                        if "by_extractor" in token_usage:
                            print("\nBreakdown by extractor/plugin:")
                            for extractor, usage in token_usage["by_extractor"].items():
                                print(f"  {extractor}:")
                                print(f"    Total: {usage.get('total_tokens', 0)}")
                                print(f"    Prompt: {usage.get('prompt_tokens', 0)}")
                                print(f"    Completion: {usage.get('completion_tokens', 0)}")
                    else:
                        print("\nNo token usage information available.")
                else:
                    logging.error(f"Failed to process resume: {resume_path}")
                    sys.exit(1)
            except Exception as e:
                logging.exception(f"Error processing resume: {e}")
                sys.exit(1)
    else:
        # Process all resumes
        try:
            processed_count, error_count = processor.process_all_resumes()
            
            # Log summary
            logging.info(f"Resume processing complete. Processed: {processed_count}, Errors: {error_count}")
        except Exception as e:
            logging.exception(f"Error processing resumes: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
