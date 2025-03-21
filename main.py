from utils.logging_utils import setup_logging
from resume_processor import ResumeProcessor
import config
import logging
import os
import sys

def main():
    # Set up logging
    setup_logging()
    
    # Create a resume processor using config directories
    processor = ResumeProcessor(
        resume_dir=config.RESUME_DIR,
        output_dir=config.OUTPUT_DIR
    )
    
    # Process all resumes
    processed_count, error_count = processor.process_all_resumes()
    
    # Log summary
    logging.info(f"Resume processing complete. Processed: {processed_count}, Errors: {error_count}")

if __name__ == "__main__":
    main()
