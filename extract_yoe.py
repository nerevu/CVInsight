# from langchain.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pypdf_test import extract_text_from_pdf
from datetime import date
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional
from pydantic import BaseModel, Field

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
    
    return f"{years} Years {months} Months"

pdf_file_path = "./Resumes/Nitesh Kumar1.pdf"
extracted_text = extract_text_from_pdf(pdf_file_path)

class WorkDates(BaseModel):
    oldest_working_date: Optional[str] = Field(
        description="The oldest working date from the resume in dd/mm/yyyy format."
    )
    newest_working_date: Optional[str] = Field(
        description="The newest working date from the resume in dd/mm/yyyy format (the end date of last company)"
    )

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
# llm = Ollama(model="gemma3:27b", base_url="https://1066-104-196-29-218.ngrok-free.app/")

chain = prompt | llm | parser

result = chain.invoke({
    "text": extracted_text,
    "month": month_text,
    "year": year
})
print("Raw output:", result)

experience = calculate_experience(result)
print("Total Experience:", experience)

