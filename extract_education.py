from pypdf_test import extract_text_from_pdf
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import date

pdf_file_path = "./Resumes/Keshav Resume.pdf"  # Replace with your PDF file path
extracted_text = extract_text_from_pdf(pdf_file_path)

today = date.today()

class Education(BaseModel):
    institution: str
    start_date: str   
    end_date: str     
    location: str
    degree: str

class ResumeEducation(BaseModel):
    educations: List[Education]

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
# llm = Ollama(model="gemma3:27b", base_url="https://1066-104-196-29-218.ngrok-free.app/", format="json")

chain = prompt | llm | parser

result = chain.invoke({"text":extracted_text, "today":today})
print("Output:", result)