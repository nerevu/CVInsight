import os
import logging
import concurrent.futures
import json
from datetime import datetime
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
    
    def __init__(self, resume_dir: str = "./Resumes", output_dir: str = "./Results", log_dir: str = "./logs/token_usage"):
        """
        Initialize the ResumeProcessor.
        
        Args:
            resume_dir: Directory containing resume files to process
            output_dir: Directory to save processed results
            log_dir: Directory to save token usage logs
        """
        self.resume_dir = resume_dir
        self.output_dir = output_dir
        self.log_dir = log_dir
        
        # Create extractors
        self.profile_extractor = ProfileExtractor()
        self.skills_extractor = SkillsExtractor()
        self.education_extractor = EducationExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.yoe_extractor = YoeExtractor()
        
        # Ensure output directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
    
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
            
            # Initialize token usage dictionary
            total_token_usage = {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "by_extractor": {},
                "source": "multiple"
            }
            
            # Extract information concurrently
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_profile = executor.submit(self.profile_extractor.extract, extracted_text)
                future_skills = executor.submit(self.skills_extractor.extract, extracted_text)
                future_education = executor.submit(self.education_extractor.extract, extracted_text)
                future_experience = executor.submit(self.experience_extractor.extract, extracted_text)
                future_yoe = executor.submit(self.yoe_extractor.extract, extracted_text)
                
                # Get results and token usage
                profile, profile_token_usage = future_profile.result()
                skills, skills_token_usage = future_skills.result()
                education, education_token_usage = future_education.result()
                experience, experience_token_usage = future_experience.result()
                yoe, yoe_token_usage = future_yoe.result()
            
            logging.debug(f"Extraction completed for {file_basename}")
            
            # Flag to check if we're using estimation for any extractor
            is_using_estimation = False
            
            # Aggregate token usage
            for extractor_usage in [profile_token_usage, skills_token_usage, education_token_usage, 
                                   experience_token_usage, yoe_token_usage]:
                extractor_name = extractor_usage.get("extractor", "unknown")
                is_estimated = extractor_usage.get("is_estimated", False)
                source = extractor_usage.get("source", "unknown")
                
                if is_estimated:
                    is_using_estimation = True
                
                total_token_usage["total_tokens"] += extractor_usage.get("total_tokens", 0)
                total_token_usage["prompt_tokens"] += extractor_usage.get("prompt_tokens", 0)
                total_token_usage["completion_tokens"] += extractor_usage.get("completion_tokens", 0)
                
                # Store by extractor for detailed breakdown
                total_token_usage["by_extractor"][extractor_name] = {
                    "total_tokens": extractor_usage.get("total_tokens", 0),
                    "prompt_tokens": extractor_usage.get("prompt_tokens", 0),
                    "completion_tokens": extractor_usage.get("completion_tokens", 0),
                    "source": source
                }
            
            # If any extractor is using estimation, mark the overall usage as estimated
            if is_using_estimation:
                total_token_usage["is_estimated"] = True
                total_token_usage["source"] = "estimation"
            
            logging.info(f"Total tokens used for {file_basename}: {total_token_usage['total_tokens']}")
            
            # Create a Resume object from the extracted information
            resume = Resume.from_extractors_output(
                profile, skills, education, experience, yoe, pdf_file_path, total_token_usage
            )
            
            return resume
            
        except Exception as e:
            logging.exception(f"Error processing resume {file_basename}: {e}")
            return None
    
    def save_token_usage(self, resume: Resume) -> Optional[str]:
        """
        Save token usage information to a separate JSON file in the log directory.
        
        Args:
            resume: The Resume object containing token usage information
            
        Returns:
            Path to the log file if successful, None otherwise
        """
        try:
            if not resume.token_usage:
                logging.warning(f"No token usage information available for {resume.file_name}")
                return None
                
            # Create a timestamp for the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            resume_name = os.path.splitext(resume.file_name)[0]
            
            # Create the token usage log filename
            log_filename = f"{resume_name}_token_usage_{timestamp}.json"
            log_file_path = os.path.join(self.log_dir, log_filename)
            
            # Add some metadata to the token usage information
            token_usage_data = {
                "resume_file": resume.file_name,
                "processed_at": timestamp,
                "token_usage": resume.token_usage
            }
            
            # Write the token usage information to a JSON file
            with open(log_file_path, 'w') as f:
                json.dump(token_usage_data, f, indent=2)
            
            logging.info(f"Token usage information saved to {log_file_path}")
            return log_file_path
            
        except Exception as e:
            logging.exception(f"Error saving token usage information for {resume.file_name}: {e}")
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
            
            # Save token usage to a separate file
            log_file_path = self.save_token_usage(resume)
            
            # Save resume data to a JSON file
            with open(output_file_path, 'w') as f:
                json.dump(resume.to_dict(), f, indent=2)
            
            logging.info(f"Results saved to {output_file_path}")
            
            # Include log file path in report if available
            self.print_token_usage_report(resume, log_file_path)
            
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
        
        # Track tokens across all resumes
        total_tokens_used = 0
        tokens_by_resume = {}
        token_usage_files = {}
        
        # Process each resume
        for pdf_file in pdf_files:
            pdf_file_path = os.path.join(self.resume_dir, pdf_file)
            
            logging.info(f"Processing {pdf_file}...")
            resume = self.process_resume(pdf_file_path)
            
            if resume:
                # Save the resume and token usage information
                if self.save_resume(resume):
                    processed_count += 1
                    
                    # Track token usage
                    tokens_used = resume.token_usage.get("total_tokens", 0)
                    total_tokens_used += tokens_used
                    tokens_by_resume[pdf_file] = tokens_used
                else:
                    error_count += 1
            else:
                logging.error(f"Failed to process {pdf_file}")
                error_count += 1
        
        # Log token usage summary
        if processed_count > 0:
            logging.info(f"Token usage summary:")
            logging.info(f"Total tokens used across all resumes: {total_tokens_used}")
            logging.info(f"Average tokens per resume: {total_tokens_used / processed_count:.2f}")
            
            # Log individual resume token usage
            for pdf_file, tokens in sorted(tokens_by_resume.items(), key=lambda x: x[1], reverse=True):
                logging.info(f"  {pdf_file}: {tokens} tokens")
            
            # Log where token usage details are stored
            logging.info(f"Detailed token usage information stored in {self.log_dir}/")
        
        logging.info(f"Processing complete. Successfully processed {processed_count} resume(s), {error_count} error(s).")
        return processed_count, error_count
    
    def print_token_usage_report(self, resume, log_file_path=None):
        """
        Print a detailed report of the token usage.
        
        Args:
            resume: Resume object containing token usage information
            log_file_path: Optional path to the token usage log file
        """
        if not resume or not resume.token_usage:
            logging.warning("No token usage information available to generate report.")
            return
        
        token_usage = resume.token_usage
        total_tokens = token_usage.get("total_tokens", 0)
        prompt_tokens = token_usage.get("prompt_tokens", 0)
        completion_tokens = token_usage.get("completion_tokens", 0)
        by_extractor = token_usage.get("by_extractor", {})
        token_source = token_usage.get("source", "unknown")
        is_estimated = token_usage.get("is_estimated", False)
        
        print(f"\n===== TOKEN USAGE REPORT FOR {resume.file_name} =====")
        print(f"Total tokens: {total_tokens}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Completion tokens: {completion_tokens}")
        
        if is_estimated:
            print("Note: Token counts are estimated (not provided by API)")
        else:
            print(f"Source: {token_source}")
        
        print("\nBreakdown by extractor:")
        # Sort extractors by token usage (highest first)
        sorted_extractors = sorted(
            by_extractor.items(), 
            key=lambda x: x[1].get("total_tokens", 0), 
            reverse=True
        )
        
        # Show top 3 extractors for a cleaner report, unless debugging
        extractors_to_show = sorted_extractors[:3]
        
        for extractor_name, extractor_usage in extractors_to_show:
            extractor_tokens = extractor_usage.get("total_tokens", 0)
            extractor_prompt = extractor_usage.get("prompt_tokens", 0)
            extractor_completion = extractor_usage.get("completion_tokens", 0)
            percentage = (extractor_tokens / total_tokens * 100) if total_tokens > 0 else 0
            source = extractor_usage.get("source", "unknown")
            
            print(f"  {extractor_name}: {extractor_tokens} tokens ({percentage:.1f}%)")
            print(f"    Prompt: {extractor_prompt}, Completion: {extractor_completion}")
        
        if log_file_path:
            print(f"\nDetailed token usage saved to: {log_file_path}")
        print("=============================================") 