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
    
    def process_output(self, output: Any) -> Dict[str, Any]:
        return self.process_list_output(output, "work_experiences") 