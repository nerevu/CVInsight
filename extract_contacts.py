from pypdf_test import extract_text_from_pdf
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import date

pdf_file_path = "./Resumes/Keshav Resume.pdf"  # Replace with your PDF file path
extracted_text = extract_text_from_pdf(pdf_file_path)

today = date.today()

class ContactInfo(BaseModel):
    contact_number: Optional[str]
    email: Optional[str]

parser = JsonOutputParser(pydantic_object=ContactInfo)

prompt_template = """
You are an expert resume parser. Your task is to extract the contact information from the resume text provided below. Specifically, extract the following details:
- Contact Number: A 10 digit phone number that may include the country code +91 (with or without spaces/dashes). Don't extract the country code.
- Email: A valid email address.

If either the contact number or email is not present in the resume, return null for that field.

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