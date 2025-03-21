from pypdf_test import extract_text_from_pdf
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

pdf_file_path = "./Resumes/Keshav Resume.pdf"  # Replace with your PDF file path
extracted_text = extract_text_from_pdf(pdf_file_path)

class Skills(BaseModel):
    skills: List[str] = Field(
        ..., 
        description="A list of skills extracted from the resume text."
    )

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
# llm = Ollama(model="gemma3:27b", base_url="https://1066-104-196-29-218.ngrok-free.app/", format="json")

chain = prompt | llm | parser

result = chain.invoke({"text":extracted_text})
print("Raw output:", result)
