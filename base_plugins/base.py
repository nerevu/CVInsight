"""
Base Plugin for Resume Analysis

This module defines the BasePlugin abstract class that all plugins must inherit from.
"""
import abc
from typing import Dict, List, Any, Type
from pydantic import BaseModel

class BasePlugin(abc.ABC):
    """
    Abstract base class for all Resume Analysis plugins.
    
    All plugins must inherit from this class and implement its abstract methods.
    """
    
    def __init__(self, llm_service):
        """
        Initialize the plugin with a language model service.
        
        Args:
            llm_service: The language model service to use for extraction.
        """
        self.llm_service = llm_service
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Get the name of the plugin.
        
        Returns:
            The plugin name.
        """
        pass
    
    @property
    @abc.abstractmethod
    def version(self) -> str:
        """
        Get the version of the plugin.
        
        Returns:
            The plugin version.
        """
        pass
    
    @property
    @abc.abstractmethod
    def description(self) -> str:
        """
        Get the description of the plugin.
        
        Returns:
            The plugin description.
        """
        pass
    
    @property
    @abc.abstractmethod
    def category(self) -> str:
        """
        Get the category of the plugin.
        
        Returns:
            The plugin category.
        """
        pass
    
    @property
    def author(self) -> str:
        """
        Get the author of the plugin.
        
        Returns:
            The plugin author.
        """
        return "Resume Analysis Team"
    
    @abc.abstractmethod
    def get_model(self) -> Type[BaseModel]:
        """
        Get the Pydantic model for the plugin.
        
        Returns:
            The Pydantic model class.
        """
        pass
    
    @abc.abstractmethod
    def get_prompt_template(self) -> str:
        """
        Get the prompt template for the plugin.
        
        Returns:
            The prompt template string.
        """
        pass
    
    def get_input_variables(self) -> List[str]:
        """
        Get the input variables for the prompt template.
        
        Returns:
            The list of input variable names.
        """
        return ["text"]
    
    def prepare_input_data(self, text: str) -> Dict[str, Any]:
        """
        Prepare the input data for the LLM.
        
        Args:
            text: The text to analyze.
            
        Returns:
            A dictionary of input data.
        """
        return {"text": text}
    
    @abc.abstractmethod
    def process_output(self, output: Any) -> Dict[str, Any]:
        """
        Process the output from the LLM.
        
        Args:
            output: The output from the LLM.
            
        Returns:
            A dictionary with the processed output.
        """
        pass
    
    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract information from text.
        
        Args:
            text: The text to extract information from.
            
        Returns:
            A dictionary containing the extracted information.
        """
        # Prepare input data
        input_data = self.prepare_input_data(text)
        
        # Generate prompt with format instructions
        parser = self.llm_service.get_json_parser(self.get_model())
        prompt = self.get_prompt_template().format(
            **input_data,
            format_instructions=parser.get_format_instructions()
        )
        
        # Generate output using the LLM
        json_output = self.llm_service.generate_text(prompt)
        
        try:
            # Parse the output
            parsed_output = parser.parse(json_output)
            return self.process_output(parsed_output)
        except Exception as e:
            print(f"Error parsing output: {e}")
            # Return empty result
            return {} 