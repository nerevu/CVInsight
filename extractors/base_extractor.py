from typing import Type, Dict, Any, List, Optional, Union
from pydantic import BaseModel
import llm_service
from abc import ABC, abstractmethod
from datetime import date

class BaseExtractor(ABC):
    """
    Base class for all extractors.
    """
    
    def __init__(self):
        """
        Initialize the extractor.
        """
        pass
    
    @abstractmethod
    def get_model(self) -> Type[BaseModel]:
        """
        Get the Pydantic model for the extractor.
        
        Returns:
            The Pydantic model class.
        """
        pass
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """
        Get the prompt template for the extractor.
        
        Returns:
            The prompt template string.
        """
        pass
    
    def get_input_variables(self) -> List[str]:
        """
        Get the input variables for the prompt template.
        Default implementation returns ["text"] which is common for most extractors.
        Override this method if additional input variables are needed.
        
        Returns:
            The list of input variable names.
        """
        return ["text"]
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        """
        Prepare the input data for the LLM.
        Default implementation returns {"text": extracted_text}.
        Override this method if additional processing or variables are needed.
        
        Args:
            extracted_text: The extracted text from the resume.
            
        Returns:
            A dictionary of input data.
        """
        input_data = {"text": extracted_text}
        
        # Add today's date if it's needed by the input variables
        if "today" in self.get_input_variables():
            input_data["today"] = date.today()
            
        return input_data
    
    def process_list_output(self, output: Any, list_field_name: str) -> Dict[str, Any]:
        """
        Process list-type output from the LLM with common pattern.
        
        Args:
            output: The output from the LLM.
            list_field_name: The name of the list field in the output.
            
        Returns:
            A dictionary with the processed output.
        """
        if isinstance(output, dict):
            items = output.get(list_field_name, [])
            # If items is already a list of dicts, return it directly
            if items and isinstance(items[0], dict):
                return {list_field_name: items}
            return {list_field_name: []}
        else:
            items = getattr(output, list_field_name, [])
            return {list_field_name: [item.model_dump() for item in items] if items else []}
    
    def process_simple_output(self, output: Any, field_names: List[str]) -> Dict[str, Any]:
        """
        Process simple output from the LLM with common pattern.
        
        Args:
            output: The output from the LLM.
            field_names: The names of the fields to extract from the output.
            
        Returns:
            A dictionary with the processed output.
        """
        result = {}
        if isinstance(output, dict):
            for field in field_names:
                result[field] = output.get(field)
        else:
            for field in field_names:
                result[field] = getattr(output, field, None)
        return result
    
    @abstractmethod
    def process_output(self, output: Any) -> Dict[str, Any]:
        """
        Process the output from the LLM.
        
        Args:
            output: The output from the LLM, which can be either a Pydantic model or a dictionary.
            
        Returns:
            A dictionary of processed output.
        """
        pass
    
    def extract(self, extracted_text: str) -> Dict[str, Any]:
        """
        Extract information from the resume.
        
        Args:
            extracted_text: The extracted text from the resume.
            
        Returns:
            A dictionary of extracted information.
        """
        input_data = self.prepare_input_data(extracted_text)
        output = llm_service.extract_with_llm(
            self.get_model(),
            self.get_prompt_template(),
            self.get_input_variables(),
            input_data
        )
        return self.process_output(output) 