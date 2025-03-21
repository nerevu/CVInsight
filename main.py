from utils import read_file, extract_profile_info, extract_education_info, extract_experience_info, extract_skills, extract_yoe
import concurrent.futures

pdf_file_path = "./Resumes/Gaurav_Kumar.pdf"
extracted_text = read_file(pdf_file_path)

def main():  
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_experiences = executor.submit(extract_experience_info, extracted_text)
        future_education = executor.submit(extract_education_info, extracted_text)
        future_yoe = executor.submit(extract_yoe, extracted_text)
        future_skills = executor.submit(extract_skills, extracted_text)
        future_profile = executor.submit(extract_profile_info, extracted_text)
        
        experiences = future_experiences.result()
        education = future_education.result()
        yoe = future_yoe.result()
        skills = future_skills.result()
        profile = future_profile.result()
    
    combined_results = {**profile, **experiences, **education, **yoe, **skills}
    
    print(combined_results)

if __name__ == "__main__":
    main()
