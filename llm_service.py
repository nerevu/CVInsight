from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from functools import lru_cache
import config
from typing import Type, Any, Dict
from pydantic import BaseModel

@lru_cache(maxsize=2)
def get_llm(model_name=None):
    """
    Get a cached LLM instance.
    
    Args:
        model_name: The name of the model to use. Defaults to config.DEFAULT_LLM_MODEL.
        
    Returns:
        A ChatGoogleGenerativeAI instance.
    """
    model = model_name or config.DEFAULT_LLM_MODEL
    return ChatGoogleGenerativeAI(api_key=config.GOOGLE_API_KEY, model=model)

def create_extraction_chain(pydantic_model: Type[BaseModel], prompt_template: str, input_variables: list):
    """
    Create a chain for extracting information using a language model.
    
    Args:
        pydantic_model: The Pydantic model to use for parsing the output.
        prompt_template: The prompt template to use.
        input_variables: The list of input variables for the prompt template.
        
    Returns:
        A chain that can be used to extract information.
    """
    parser = JsonOutputParser(pydantic_object=pydantic_model)
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=input_variables,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    llm = get_llm()
    
    return prompt | llm | parser

def extract_with_llm(pydantic_model: Type[BaseModel], prompt_template: str, 
                    input_variables: list, input_data: dict) -> Any:
    """
    Extract information from text using a language model.
    
    Args:
        pydantic_model: The Pydantic model to use for parsing the output.
        prompt_template: The prompt template to use.
        input_variables: The list of input variables for the prompt template.
        input_data: The input data to pass to the prompt template.
        
    Returns:
        The extracted information as a Pydantic model instance or a dictionary.
    """
    try:
        chain = create_extraction_chain(pydantic_model, prompt_template, input_variables)
        result = chain.invoke(input_data)
        
        # If result is already a dictionary or a Pydantic model, return it directly
        if isinstance(result, dict) or isinstance(result, pydantic_model):
            return result
            
        # If we got here, something unexpected happened. Return an empty model.
        return pydantic_model()
        
    except Exception as e:
        print(f"Error extracting information with LLM: {e}")
        # Return an empty dictionary that matches the expected structure of the model
        return {} 