from utils.common import read_file
from extractors.profile_extractor import ProfileExtractor
from extractors.skills_extractor import SkillsExtractor
from extractors.education_extractor import EducationExtractor
from extractors.experience_extractor import ExperienceExtractor
from extractors.yoe_extractor import YoeExtractor
import concurrent.futures
import os
import json

def main():  
    # Get the resume file path
    pdf_file_path = "./Resumes/Gaurav_Kumar.pdf"
    
    # Check if file exists
    if not os.path.exists(pdf_file_path):
        print(f"Error: File not found at {pdf_file_path}")
        return
    
    try:
        # Extract text from the resume
        extracted_text = read_file(pdf_file_path)
        
        # Create extractors
        profile_extractor = ProfileExtractor()
        skills_extractor = SkillsExtractor()
        education_extractor = EducationExtractor()
        experience_extractor = ExperienceExtractor()
        yoe_extractor = YoeExtractor()
        
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
        
        # Combine results
        combined_results = {**profile, **skills, **education, **experience, **yoe}
        
        # Print the results
        print(json.dumps(combined_results, indent=2))
        
    except Exception as e:
        print(f"Error processing resume: {e}")

if __name__ == "__main__":
    main()
