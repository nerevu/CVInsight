from utils.common import read_file, validate_file
from extractors.profile_extractor import ProfileExtractor
from extractors.skills_extractor import SkillsExtractor
from extractors.education_extractor import EducationExtractor
from extractors.experience_extractor import ExperienceExtractor
from extractors.yoe_extractor import YoeExtractor
import concurrent.futures
import os
import json
import logging
import config
import sys

# Configure logging
def setup_logging():
    """Set up logging configuration."""
    log_level = getattr(logging, config.LOG_LEVEL)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log startup information
    logging.info("Resume Analysis application started")

def process_resume(pdf_file_path):
    """
    Process a single resume file.
    
    Args:
        pdf_file_path: Path to the PDF resume file.
        
    Returns:
        A dictionary with extracted information from the resume or None if processing failed.
    """
    file_basename = os.path.basename(pdf_file_path)
    
    # Validate the file
    is_valid, message = validate_file(pdf_file_path)
    if not is_valid:
        logging.error(f"Validation failed for {file_basename}: {message}")
        return None
    
    try:
        logging.info(f"Extracting text from {file_basename}")
        # Extract text from the resume
        extracted_text = read_file(pdf_file_path)
        
        # Create extractors
        profile_extractor = ProfileExtractor()
        skills_extractor = SkillsExtractor()
        education_extractor = EducationExtractor()
        experience_extractor = ExperienceExtractor()
        yoe_extractor = YoeExtractor()
        
        logging.info(f"Extracting information from {file_basename}")
        # Extract information concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_profile = executor.submit(profile_extractor.extract, extracted_text)
            future_skills = executor.submit(skills_extractor.extract, extracted_text)
            future_education = executor.submit(education_extractor.extract, extracted_text)
            future_experience = executor.submit(experience_extractor.extract, extracted_text)
            future_yoe = executor.submit(yoe_extractor.extract, extracted_text)
            
            # Get results
            profile = future_profile.result()
            skills = future_skills.result()
            education = future_education.result()
            experience = future_experience.result()
            yoe = future_yoe.result()
        
        logging.debug(f"Extraction completed for {file_basename}")
        # Combine results
        return {**profile, **skills, **education, **experience, **yoe}
        
    except Exception as e:
        logging.exception(f"Error processing resume {file_basename}: {e}")
        return None

def main():
    # Set up logging
    setup_logging()
      
    # Get the resume directory path
    resume_dir = "./Resumes"
    
    # Check if directory exists
    if not os.path.exists(resume_dir):
        logging.error(f"Error: Directory not found at {resume_dir}")
        return
    
    # Create output directory if it doesn't exist
    output_dir = "./Results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PDF files in the directory
    pdf_files = [f for f in os.listdir(resume_dir) if os.path.splitext(f)[1].lower() in config.ALLOWED_FILE_EXTENSIONS]
    
    if not pdf_files:
        logging.warning(f"No PDF files found in {resume_dir}")
        return
    
    logging.info(f"Found {len(pdf_files)} resume(s) to process.")
    
    processed_count = 0
    error_count = 0
    
    # Process each resume
    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(resume_dir, pdf_file)
        
        logging.info(f"Processing {pdf_file}...")
        results = process_resume(pdf_file_path)
        
        if results:
            # Save results to a JSON file
            output_file_name = os.path.splitext(pdf_file)[0] + ".json"
            output_file_path = os.path.join(output_dir, output_file_name)
            
            try:
                with open(output_file_path, 'w') as f:
                    json.dump(results, f, indent=2)
                
                logging.info(f"Results saved to {output_file_path}")
                processed_count += 1
            except Exception as e:
                logging.exception(f"Error saving results for {pdf_file}: {e}")
                error_count += 1
        else:
            logging.error(f"Failed to process {pdf_file}")
            error_count += 1
    
    logging.info(f"Processing complete. Successfully processed {processed_count} resume(s), {error_count} error(s).")

if __name__ == "__main__":
    main()
