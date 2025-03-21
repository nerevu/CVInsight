from typing import Type, Dict, Any, List
from pydantic import BaseModel
from extractors.base_extractor import BaseExtractor
from models import ResumeWorkExperience
from datetime import date

class ExperienceExtractor(BaseExtractor):
    """
    Extractor for work experience information.
    """
    
    def get_model(self) -> Type[BaseModel]:
        return ResumeWorkExperience
    
    def get_prompt_template(self) -> str:
        return """
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
            experiences = output.get("work_experiences", [])
            # If experiences is already a list of dicts, return it directly
            if experiences and isinstance(experiences[0], dict):
                return {"work_experiences": experiences}
            return {"work_experiences": []}
        else:
            return {"work_experiences": [exp.model_dump() for exp in output.work_experiences] if output.work_experiences else []} 