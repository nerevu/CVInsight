import os
import logging
import concurrent.futures
from typing import Optional, Dict, Any, List, Tuple
from models import Resume
from extractors.profile_extractor import ProfileExtractor
from extractors.skills_extractor import SkillsExtractor
from extractors.education_extractor import EducationExtractor
from extractors.experience_extractor import ExperienceExtractor
from extractors.yoe_extractor import YoeExtractor
from utils.file_utils import read_file, validate_file
import config

class ResumeProcessor:
    """
    Class for processing resumes and extracting information.
    """
    
    def __init__(self, resume_dir: str = "./Resumes", output_dir: str = "./Results"):
        """
        Initialize the ResumeProcessor.
        
        Args:
            resume_dir: Directory containing resume files to process
            output_dir: Directory to save processed results
        """
        self.resume_dir = resume_dir
        self.output_dir = output_dir
        
        # Create extractors
        self.profile_extractor = ProfileExtractor()
        self.skills_extractor = SkillsExtractor()
        self.education_extractor = EducationExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.yoe_extractor = YoeExtractor()
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_resume_files(self) -> List[str]:
        """
        Get all resume files in the resume directory.
        
        Returns:
            A list of resume file names
        """
        if not os.path.exists(self.resume_dir):
            logging.error(f"Error: Directory not found at {self.resume_dir}")
            return []
        
        # Get all PDF files in the directory
        return [f for f in os.listdir(self.resume_dir) 
                if os.path.splitext(f)[1].lower() in config.ALLOWED_FILE_EXTENSIONS]
    
    def process_resume(self, pdf_file_path: str) -> Optional[Resume]:
        """
        Process a single resume file.
        
        Args:
            pdf_file_path: Path to the PDF resume file.
            
        Returns:
            A Resume object with extracted information or None if processing failed.
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
            
            logging.info(f"Extracting information from {file_basename}")
            # Extract information concurrently
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_profile = executor.submit(self.profile_extractor.extract, extracted_text)
                future_skills = executor.submit(self.skills_extractor.extract, extracted_text)
                future_education = executor.submit(self.education_extractor.extract, extracted_text)
                future_experience = executor.submit(self.experience_extractor.extract, extracted_text)
                future_yoe = executor.submit(self.yoe_extractor.extract, extracted_text)
                
                # Get results
                profile = future_profile.result()
                skills = future_skills.result()
                education = future_education.result()
                experience = future_experience.result()
                yoe = future_yoe.result()
            
            logging.debug(f"Extraction completed for {file_basename}")
            
            # Create a Resume object from the extracted information
            resume = Resume.from_extractors_output(
                profile, skills, education, experience, yoe, pdf_file_path
            )
            
            return resume
            
        except Exception as e:
            logging.exception(f"Error processing resume {file_basename}: {e}")
            return None
    
    def save_resume(self, resume: Resume) -> bool:
        """
        Save a processed resume to a JSON file.
        
        Args:
            resume: The Resume object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_file_name = os.path.splitext(resume.file_name)[0] + ".json"
            output_file_path = os.path.join(self.output_dir, output_file_name)
            
            with open(output_file_path, 'w') as f:
                import json
                json.dump(resume.to_dict(), f, indent=2)
            
            logging.info(f"Results saved to {output_file_path}")
            return True
            
        except Exception as e:
            logging.exception(f"Error saving results for {resume.file_name}: {e}")
            return False
    
    def process_all_resumes(self) -> Tuple[int, int]:
        """
        Process all resume files in the resume directory.
        
        Returns:
            A tuple of (processed_count, error_count)
        """
        pdf_files = self.get_resume_files()
        
        if not pdf_files:
            logging.warning(f"No PDF files found in {self.resume_dir}")
            return 0, 0
        
        logging.info(f"Found {len(pdf_files)} resume(s) to process.")
        
        processed_count = 0
        error_count = 0
        
        # Process each resume
        for pdf_file in pdf_files:
            pdf_file_path = os.path.join(self.resume_dir, pdf_file)
            
            logging.info(f"Processing {pdf_file}...")
            resume = self.process_resume(pdf_file_path)
            
            if resume:
                if self.save_resume(resume):
                    processed_count += 1
                else:
                    error_count += 1
            else:
                logging.error(f"Failed to process {pdf_file}")
                error_count += 1
        
        logging.info(f"Processing complete. Successfully processed {processed_count} resume(s), {error_count} error(s).")
        return processed_count, error_count 