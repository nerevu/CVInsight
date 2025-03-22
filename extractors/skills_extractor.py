from typing import Type, Dict, Any, List
from pydantic import BaseModel
from extractors.base_extractor import BaseExtractor
from models import Skills

class SkillsExtractor(BaseExtractor):
    """
    Extractor for skills.
    """
    
    def get_model(self) -> Type[BaseModel]:
        return Skills
    
    def get_prompt_template(self) -> str:
        return """
You are an assistant that extracts a list of skills mentioned in the text below. Only focus on Skills section of the below text.
Return your output as a JSON object with the below schema.
{format_instructions}

Text:
{text}
"""
    
    def get_input_variables(self) -> List[str]:
        return ["text"]
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        return {"text": extracted_text}
    
    def process_output(self, output: Any) -> Dict[str, Any]:
        """
        Process the output from the LLM.
        
        Args:
            output: The output from the LLM.
            
        Returns:
            A dictionary with the skills information.
        """
        return self.process_list_output(output, "skills") 