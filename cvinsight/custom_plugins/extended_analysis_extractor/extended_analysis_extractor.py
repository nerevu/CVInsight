from typing import Dict, Any, Type, List, Optional, Tuple
from datetime import datetime
import logging

from pydantic import BaseModel, Field

from cvinsight.plugins.base import ExtractorPlugin, PluginMetadata, PluginCategory


class ExtendedAnalysisData(BaseModel):
    """Simplified years of experience analysis data - only 4 YoE fields."""
    
    # Years of Experience fields with simplified names
    wyoe: Optional[float] = Field(None, description="Total years of ALL work experience")
    relevant_wyoe: Optional[float] = Field(None, description="Total years of RELEVANT work experience based on job description")
    eyoe: Optional[float] = Field(None, description="Total years of ALL education experience")
    relevant_eyoe: Optional[float] = Field(None, description="Total years of RELEVANT education experience based on job description")


class ExtendedAnalysisExtractorPlugin(ExtractorPlugin):
    """Simplified plugin that extracts only 4 years of experience fields."""

    def __init__(self, job_description: str = None, date_of_resume_submission: str = None, llm_service=None):
        """
        Initialize the plugin with optional job description and submission date.
        
        Args:
            job_description: Optional job description to determine relevance
            date_of_resume_submission: Date when the resume was submitted (for 'present' calculations)
            llm_service: LLM service for extraction
        """
        self.llm_service = llm_service
        # Always ensure we have a job description for LLM processing
        if job_description is None or job_description.strip() == "":
            self.job_description = """
            General professional position requiring:
            - Relevant work experience in any field
            - Educational background appropriate to the role
            - Professional skills and competencies
            - Ability to work effectively and contribute value
            """
        else:
            self.job_description = job_description
            
        self.date_of_resume_submission = date_of_resume_submission

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="extended_analysis_extractor",
            version="1.0.0",
            description="Simplified extractor for 4 years of experience fields: wyoe, relevant_wyoe, eyoe, relevant_eyoe.",
            category=PluginCategory.CUSTOM,
            author="AI Assistant"
        )

    def initialize(self) -> None:
        pass

    def get_model(self) -> Type[BaseModel]:
        return ExtendedAnalysisData

    def get_prompt_template(self) -> str:
        return """
        Analyze the following resume text to extract years of experience information.
        
        JOB DESCRIPTION:
        {job_description}
        
        TODAY'S DATE FOR CALCULATING PRESENT POSITIONS: {submission_date}
        
        Extract the following 4 values:

        **Education Experience:**
        - eyoe: Total years of ALL education using these EXACT guidelines:
          * Diploma/certificate: 1 year (0.5 if pursuing)
          * Associate's degree: 2 years (1 if pursuing) 
          * Bachelor's degree: 4 years (2 if pursuing)
          * Master's degree: 6 years (3 if pursuing)
          * PhD/Doctorate: 8 years (7 if pursuing)
        - relevant_eyoe: Years of RELEVANT education that directly applies to the job description.
          If education field closely matches job requirements, count full years.
          If partially relevant, count proportionally (e.g., 75%, 50%, 25%).
          If not relevant at all, count 0.
             
        **Work Experience:**
        - wyoe: Total years of ALL work experience (sum all positions)
        - relevant_wyoe: Years of RELEVANT work experience that applies to the job description.
          * Fully relevant (exact same role): 100% of time
          * Highly relevant (similar role, overlapping skills): ~75% of time  
          * Moderately relevant (different role, key skills used): ~50% of time
          * Slightly relevant (minimal skill overlap): ~25% of time
          * Not relevant (no skill overlap): 0% of time

        For positions listed as "present" or "current", calculate duration up to: {submission_date}
        Provide all output as numerical years with one decimal place (e.g., 2.5 for 2 years 6 months).

        Resume Text:
        {text}

        {format_instructions}
        """

    def get_input_variables(self) -> List[str]:
        return ["text", "job_description", "submission_date"]
        
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        # Use the current date if submission_date wasn't provided
        submission_date = self.date_of_resume_submission or datetime.now().strftime("%Y-%m-%d")
        
        return {
            "text": extracted_text,
            "job_description": self.job_description,
            "submission_date": submission_date
        }

    def process_output(self, result: Any) -> Dict[str, Any]:
        """Process the LLM output and ensure all 4 YoE fields are present."""
        if isinstance(result, ExtendedAnalysisData):
            result_dict = result.model_dump()
        else:
            result_dict = result
            
        # Ensure all required fields are present with proper defaults
        if "wyoe" not in result_dict or result_dict["wyoe"] is None:
            result_dict["wyoe"] = 0.0
        if "eyoe" not in result_dict or result_dict["eyoe"] is None:
            result_dict["eyoe"] = 0.0
        if "relevant_wyoe" not in result_dict or result_dict["relevant_wyoe"] is None:
            result_dict["relevant_wyoe"] = 0.0
        if "relevant_eyoe" not in result_dict or result_dict["relevant_eyoe"] is None:
            result_dict["relevant_eyoe"] = 0.0
                
        return result_dict

    def extract(self, text: str, additional_params: Dict[str, Any] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract years of experience information from text.
        
        Args:
            text: The text to extract information from.
            additional_params: Optional additional parameters like date_of_resume_submission or job_description
            
        Returns:
            A tuple of (extracted_data, token_usage)
        """
        import logging
        
        # Set temporary job_description and date_of_resume_submission if provided in additional_params
        original_job_description = self.job_description
        original_date = self.date_of_resume_submission
        
        if additional_params:
            logging.info(f"Received additional parameters: {additional_params.keys()}")
            if additional_params.get("job_description"):
                self.job_description = additional_params["job_description"]
                logging.info(f"Using job description from additional parameters")
            if additional_params.get("date_of_resume_submission"):
                self.date_of_resume_submission = additional_params["date_of_resume_submission"]
                logging.info(f"Using submission date from additional parameters: {self.date_of_resume_submission}")
        
        # Always use LLM processing to get years of experience analysis
        if not self.job_description or self.job_description.strip() == "":
            logging.info("No specific job description provided - using default")
            self.job_description = """
            General professional position requiring:
            - Relevant work experience in any field
            - Educational background appropriate to the role
            - Professional skills and competencies
            - Ability to work effectively and contribute value
            """
        
        # Prepare prompt from template for LLM extraction
        prompt_template = self.get_prompt_template()
        input_data = self.prepare_input_data(text)
        input_variables = self.get_input_variables()
        model = self.get_model()
        
        try:
            # Call LLM service
            result, token_usage = self.llm_service.extract_with_llm(
                model,
                prompt_template,
                input_variables,
                input_data
            )
            
            # Add extractor name to token usage
            token_usage["extractor"] = self.metadata.name
            
            # Log the raw LLM result
            logging.info(f"Raw LLM result for YoE analysis: {result}")
            
            # Process the result using the process_output method
            processed_result = self.process_output(result)
            
            # Log the extracted result
            logging.info(f"Extracted YoE analysis: {processed_result}")
            
            return processed_result, token_usage
            
        finally:
            # Restore original values
            self.job_description = original_job_description
            self.date_of_resume_submission = original_date
