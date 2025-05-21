from typing import Dict, Any, Type, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field

from cvinsight.plugins.base import ExtractorPlugin, PluginMetadata, PluginCategory

class SeniorityLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid-level"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"
    INTERN = "intern"
    UNKNOWN = "unknown"

class WorkStatistics(BaseModel):
    """Statistics about the candidate's work experience."""
    highest_seniority_level: Optional[SeniorityLevel] = Field(SeniorityLevel.UNKNOWN, description="Highest seniority level achieved (e.g., junior, mid, senior, exec)." )
    primary_position_title: Optional[str] = Field(None, description="The most common or highest-ranking job title that best describes the candidate's primary role.")
    average_tenure_at_company_years: Optional[float] = Field(None, description="Average length of time in years spent at each company (place of work, not individual roles within the same company).")

class WorkStatsExtractorPlugin(ExtractorPlugin):
    """Plugin to extract statistics about a candidate's work experience."""

    def __init__(self, llm_service=None):
        self.llm_service = llm_service

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="work_stats_extractor",
            version="1.0.0",
            description="Extracts work statistics like highest seniority, primary title, and average tenure per company.",
            category=PluginCategory.CUSTOM,
            author="AI Assistant"
        )

    def initialize(self) -> None:
        pass

    def get_model(self) -> Type[BaseModel]:
        return WorkStatistics

    def get_prompt_template(self) -> str:
        return """
        Analyze the work experience section of the following resume text.
        Determine the following:
        1.  Highest seniority level achieved by the candidate. Categorize as one of: {seniority_levels}.
        2.  The primary position title that best describes the candidate's overall professional role or highest achieved role.
        3.  The average length of time (in years, e.g., 2.5 for 2 years and 6 months) the candidate spent at each company (place of work). If multiple roles exist at the same company, count it as one continuous period for that company.

        Resume Text:
        {text}

        {format_instructions}
        """

    def get_input_variables(self) -> List[str]:
        return ["text", "seniority_levels"]

    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        return {
            "text": extracted_text,
            "seniority_levels": ", ".join([s.value for s in SeniorityLevel if s != SeniorityLevel.UNKNOWN])
        }
        
    def process_output(self, result: Any) -> Dict[str, Any]:
        if isinstance(result, WorkStatistics):
            return result.model_dump()
        return result
        
    def extract(self, text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract work statistics from text.
        
        Args:
            text: The text to extract information from.
            
        Returns:
            A tuple of (extracted_data, token_usage)
        """
        # Prepare prompt from template
        prompt_template = self.get_prompt_template()
        input_data = self.prepare_input_data(text)
        input_variables = self.get_input_variables()
        model = self.get_model()
        
        # Call LLM service
        result, token_usage = self.llm_service.extract_with_llm(
            model,
            prompt_template,
            input_variables,
            input_data
        )
        
        # Add extractor name to token usage
        token_usage["extractor"] = self.metadata.name
        
        # Process the result
        processed_result = self.process_output(result)
        
        return processed_result, token_usage
