from typing import Dict, Any, Type, List, Optional, Tuple

from pydantic import BaseModel, Field
from enum import Enum

from cvinsight.plugins.base import ExtractorPlugin, PluginMetadata, PluginCategory

class DegreeStatus(str, Enum):
    COMPLETED = "completed"
    PURSUING = "pursuing"
    UNKNOWN = "unknown"

class SchoolPrestige(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"

class EducationStats(BaseModel):
    """Statistics about the candidate's education."""
    highest_degree: Optional[str] = Field(None, description="The highest academic degree obtained or being pursued.")
    highest_degree_status: Optional[DegreeStatus] = Field(DegreeStatus.UNKNOWN, description="Indicates whether the highest degree is completed or currently being pursued.")
    highest_degree_major: Optional[str] = Field(None, description="The major or field of study for the highest degree.")
    highest_degree_school_prestige: Optional[SchoolPrestige] = Field(SchoolPrestige.UNKNOWN, description="Prestige level of the school for the highest degree (low, medium, high). Example: low for public/online, medium for mid-level university, high for prestigious university")

class EducationStatsExtractorPlugin(ExtractorPlugin):
    """Plugin to extract statistics about a candidate's education."""

    def __init__(self, llm_service=None):
        self.llm_service = llm_service

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="education_stats_extractor",
            version="1.0.0",
            description="Extracts statistics about a candidate's education, including highest degree, status, major, and school prestige.",
            category=PluginCategory.CUSTOM,
            author="AI Assistant"
        )

    def initialize(self) -> None:
        pass

    def get_model(self) -> Type[BaseModel]:
        return EducationStats

    def get_prompt_template(self) -> str:
        return """
        Analyze the education section of the following resume text.
        Identify the following:
        1.  The highest academic degree the candidate has obtained or is currently pursuing (e.g., PhD, Master of Science, Bachelor of Arts, Associate Degree).
        2.  The status of this highest degree: 'completed' or 'pursuing'.
        3.  The major or field of study for this highest degree (e.g., Computer Science, Mechanical Engineering, Business Administration).
        4.  The prestige level of the institution for this highest degree. Categorize as 'low' (e.g., community colleges, online-only unaccredited institutions), 'medium' (e.g., most public universities, accredited private universities), or 'high' (e.g., Ivy League, top-tier internationally recognized universities).

        Resume Text:
        {text}

        {format_instructions}
        """

    def get_input_variables(self) -> List[str]:
        return ["text"]

    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        return {"text": extracted_text}
        
    def process_output(self, result: Any) -> Dict[str, Any]:
        if isinstance(result, EducationStats):
            return result.model_dump()
        return result
        
    def extract(self, text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract education statistics from text.
        
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
