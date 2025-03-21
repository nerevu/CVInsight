from typing import Type, Dict, Any, List
from pydantic import BaseModel
from extractors.base_extractor import BaseExtractor
from models import WorkDates
from datetime import date
from utils.common import calculate_experience

class YoeExtractor(BaseExtractor):
    """
    Extractor for years of experience.
    """
    
    def get_model(self) -> Type[BaseModel]:
        """
        Get the Pydantic model for the extractor.
        
        Returns:
            The WorkDates model class.
        """
        return WorkDates
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template for the extractor.
        
        Returns:
            The prompt template string.
        """
        return """
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
    
    def get_input_variables(self) -> List[str]:
        """
        Get the input variables for the prompt template.
        
        Returns:
            The list of input variable names.
        """
        return ["text", "month", "year"]
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        """
        Prepare the input data for the LLM.
        
        Args:
            extracted_text: The extracted text from the resume.
            
        Returns:
            A dictionary of input data.
        """
        today = date.today()
        month_text = today.strftime("%B")
        year = today.year
        
        return {
            "text": extracted_text,
            "month": month_text,
            "year": year
        }
    
    def process_output(self, output: Any) -> Dict[str, Any]:
        """
        Process the output from the LLM.
        
        Args:
            output: The output from the LLM.
            
        Returns:
            A dictionary with the years of experience.
        """
        if isinstance(output, dict):
            oldest_date = output.get("oldest_working_date")
            newest_date = output.get("newest_working_date")
        else:
            oldest_date = output.oldest_working_date
            newest_date = output.newest_working_date
            
        experience = calculate_experience(oldest_date, newest_date)
        return {"YoE": experience} 