from typing import Type, Dict, Any, List
from pydantic import BaseModel
from extractors.base_extractor import BaseExtractor
from models import ResumeEducation
from datetime import date

class EducationExtractor(BaseExtractor):
    """
    Extractor for education information.
    """
    
    def get_model(self) -> Type[BaseModel]:
        return ResumeEducation
    
    def get_prompt_template(self) -> str:
        return """
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
    
    def get_input_variables(self) -> List[str]:
        return ["text", "today"]
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        today = date.today()
        return {
            "text": extracted_text,
            "today": today
        }
    
    def process_output(self, output: Any) -> Dict[str, Any]:
        if isinstance(output, dict):
            educations = output.get("educations", [])
            # If educations is already a list of dicts, return it directly
            if educations and isinstance(educations[0], dict):
                return {"educations": educations}
            return {"educations": []}
        else:
            return {"educations": [edu.model_dump() for edu in output.educations] if output.educations else []} 