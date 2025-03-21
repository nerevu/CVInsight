import PyPDF2
from datetime import date
from pypdf_test import extract_text_from_pdf
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from datetime import datetime

# ocr = OCRProcessor(model_name='gemma3:27b', base_url="https://1066-104-196-29-218.ngrok-free.app/api/generate")

# nltk.download('stopwords', quiet=True)
# stop_words = set(stopwords.words('english'))
# punctuation = string.punctuation

def read_file(file_path):
    """
    Reads a file and extracts the text.
    """
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

class Skills(BaseModel):
    skills: List[str] = Field(
        ...,
        description="A list of skills extracted from the resume text."
    )

def extract_skills(extracted_text):
    """
    Extracts skills from a resume using a language model.
    """
    parser = JsonOutputParser(pydantic_object=Skills)

    prompt_template = """
You are an assistant that extracts a list of skills mentioned in the text below. Only focus on Skills section of the below text.
Return your output as a JSON object with the below schema.
{format_instructions}

Text:
{text}
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    llm = ChatGoogleGenerativeAI(api_key="AIzaSyCgBrEbvU8Tp6bOsHEXQ5kmJ-4v4l0T3So", model="gemini-2.0-flash")

    chain = prompt | llm | parser

    result = chain.invoke({"text": extracted_text})
    return result

class WorkDates(BaseModel):
    oldest_working_date: Optional[str] = Field(
        description="The oldest working date from the resume in dd/mm/yyyy format."
    )
    newest_working_date: Optional[str] = Field(
        description="The newest working date from the resume in dd/mm/yyyy format (the end date of last company)"
    )

def calculate_experience(experience_dates):
    """
    Calculate total years of experience between oldest_working_date and newest_working_date.
    The dates should be in "dd/mm/yyyy" format.
    
    Parameters:
      experience_dates (dict): A dictionary with keys "oldest_working_date" and "newest_working_date".
    
    Returns:
      str: A string representing the total experience in "X Years Y Months" format.
    """
    oldest_str = experience_dates.get("oldest_working_date")
    newest_str = experience_dates.get("newest_working_date")
    
    if not oldest_str or not newest_str:
        return "0 Years 0 Months"
    
    # Define the expected date format.
    date_format = "%d/%m/%Y"
    try:
        oldest_date = datetime.strptime(oldest_str, date_format)
        newest_date = datetime.strptime(newest_str, date_format)
    except ValueError:
        # If the date format is invalid, return default experience.
        return "0 Years 0 Months"
    
    # Calculate total months of difference.
    total_months = (newest_date.year - oldest_date.year) * 12 + (newest_date.month - oldest_date.month)
    
    # Adjust if the day of the month in the newest date is less than the oldest date.
    if newest_date.day < oldest_date.day:
        total_months -= 1
    
    years = total_months // 12
    months = total_months % 12
    
    return {"YoE": f"{years} Years {months} Months"}

def extract_yoe(extracted_text):
    """
    Extracts years of experience from a resume using a language model.
    """
    today = date.today()
    month_text = today.strftime("%B")
    year = today.year

    parser = JsonOutputParser(pydantic_object=WorkDates)

    prompt_template = """
You are a resume analysis assistant. Your task is to extract the oldest working date and the newest working date (the end date of the last company) from the "Work Experience" section of a candidate's resume. Follow these guidelines:

- Dates must be in the format dd/mm/yyyy. If the day is missing, use "01".
- Only consider dates found in the "Work Experience" section.
- If no such section or dates exist, return null for both values.

Return your output as a JSON object with the keys "oldest_working_date" and "newest_working_date".
{format_instructions}

Current date: {month}, {year}

Resume Text:
{text}

"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["text", "month", "year"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    llm = ChatGoogleGenerativeAI(api_key="AIzaSyCgBrEbvU8Tp6bOsHEXQ5kmJ-4v4l0T3So", model="gemini-2.0-flash")

    chain = prompt | llm | parser

    result = chain.invoke({
        "text": extracted_text,
        "month": month_text,
        "year": year
    })

    experience = calculate_experience(result)
    return experience

class ProfileInfo(BaseModel):
    name: Optional[str]
    contact_number: Optional[str]
    email: Optional[str]

def extract_profile_info(extracted_text):
    """
    Extracts contact information from a resume using a language model.
    """
    today = date.today()

    parser = JsonOutputParser(pydantic_object=ProfileInfo)

    prompt_template = """
You are an expert resume parser. Your task is to extract the contact information from the resume text provided below. Specifically, extract the following details:
- Name: Name of the candidate.
- Contact Number: A 10 digit phone number that may include the country code +91 (with or without spaces/dashes). Don't extract the country code.
- Email: A valid email address.

If any of the name, contact number or email is not present in the resume, return null for that field.

Return your output as a JSON object with the below schema.
{format_instructions}

Text:
{text}
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["text", "today"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    llm = ChatGoogleGenerativeAI(api_key="AIzaSyCgBrEbvU8Tp6bOsHEXQ5kmJ-4v4l0T3So", model="gemini-2.0-flash")

    chain = prompt | llm | parser

    result = chain.invoke({"text":extracted_text, "today":today})
    return result

class WorkExperience(BaseModel):
    company: str
    start_date: str
    end_date: str  
    location: str
    role: str

class ResumeWorkExperience(BaseModel):
    work_experiences: List[WorkExperience]

def extract_experience_info(extracted_text):
    """
    Extracts work experience details from a resume using a language model.
    """
    today = date.today()

    parser = JsonOutputParser(pydantic_object=ResumeWorkExperience)

    prompt_template = """
You are an expert resume parser. Your task is to extract work experience details from the resume text provided below. For each work experience entry, extract the following details:
- Company
- Start Date: in dd/mm/yyyy format. If the resume does not provide the day or month, default the missing parts to "01". If you encounter Present then use the current date, i.e. {today}.
- End Date: in dd/mm/yyyy format. If the resume does not provide the day or month, default the missing parts to "01". If you encounter Present then use the current date, i.e. {today}.
- Location
- Role
Only focus on Work Experience section of the below text. If you cannot find anything, return null.

Return your output as a JSON object with the below schema.
{format_instructions}

Text:
{text}
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["text", "today"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    llm = ChatGoogleGenerativeAI(api_key="AIzaSyCgBrEbvU8Tp6bOsHEXQ5kmJ-4v4l0T3So", model="gemini-2.0-flash")

    chain = prompt | llm | parser

    result = chain.invoke({"text":extracted_text, "today":today})
    return result

class Education(BaseModel):
    institution: str
    start_date: str   
    end_date: str     
    location: str
    degree: str

class ResumeEducation(BaseModel):
    educations: List[Education]

def extract_education_info(extracted_text):
    """
    Extracts education details from a resume using a language model.
    """
    today = date.today()

    parser = JsonOutputParser(pydantic_object=ResumeEducation)

    prompt_template = """
You are an expert resume parser. Your task is to extract education details from the resume text provided below. For each education entry, extract the following details:
- College/School (output as "institution")
- Start Date: If mentioned, convert it into the dd/mm/yyyy format. If the day is missing, default it to "01". If the month is missing, default it to "06". If no start date is mentioned, return null. If you encounter Present then use the current date, i.e. {today}.
- End Date: If mentioned, convert it into the dd/mm/yyyy format. If the day is missing, default it to "01". If the month is missing, default it to "06". If no end date is mentioned, return null. If you encounter Present then use the current date, i.e. {today}.
- Location
- Degree
Only focus on Education section of the below text. If you cannot find anything, return null.

Return your output as a JSON object with the below schema.
{format_instructions}

Text:
{text}
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["text", "today"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    llm = ChatGoogleGenerativeAI(api_key="AIzaSyCgBrEbvU8Tp6bOsHEXQ5kmJ-4v4l0T3So", model="gemini-2.0-flash")
    # llm = Ollama(model="gemma3:27b", base_url="https://1066-104-196-29-218.ngrok-free.app/")

    chain = prompt | llm | parser

    result = chain.invoke({"text":extracted_text, "today":today})
    return result
