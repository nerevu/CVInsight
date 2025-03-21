from typing import Type, Dict, Any, List
from pydantic import BaseModel
import llm_service
from abc import ABC, abstractmethod

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
    
    @abstractmethod
    def get_input_variables(self) -> List[str]:
        """
        Get the input variables for the prompt template.
        
        Returns:
            The list of input variable names.
        """
        pass
    
    @abstractmethod
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        """
        Prepare the input data for the LLM.
        
        Args:
            extracted_text: The extracted text from the resume.
            
        Returns:
            A dictionary of input data.
        """
        pass
    
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