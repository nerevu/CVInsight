from typing import Type, Dict, Any, List
from pydantic import BaseModel
from extractors.base_extractor import BaseExtractor
from models import ProfileInfo
from datetime import date

class ProfileExtractor(BaseExtractor):
    """
    Extractor for profile information.
    """
    
    def get_model(self) -> Type[BaseModel]:
        """
        Get the Pydantic model for the extractor.
        
        Returns:
            The ProfileInfo model class.
        """
        return ProfileInfo
    
    def get_prompt_template(self) -> str:
        """
        Get the prompt template for the extractor.
        
        Returns:
            The prompt template string.
        """
        return """
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
    
    def get_input_variables(self) -> List[str]:
        """
        Get the input variables for the prompt template.
        
        Returns:
            The list of input variable names.
        """
        return ["text"]
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        """
        Prepare the input data for the LLM.
        
        Args:
            extracted_text: The extracted text from the resume.
            
        Returns:
            A dictionary of input data.
        """
        return {
            "text": extracted_text
        }
    
    def process_output(self, output: Any) -> Dict[str, Any]:
        """
        Process the output from the LLM.
        
        Args:
            output: The output from the LLM.
            
        Returns:
            A dictionary with the profile information.
        """
        return self.process_simple_output(output, ["name", "contact_number", "email"]) 