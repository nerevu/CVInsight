from typing import Dict, Any, Type, List, Tuple
from pydantic import BaseModel
from ...plugins.base import ExtractorPlugin, PluginMetadata, PluginCategory
from ...models import ResumeWorkExperience
from datetime import date
import logging

class ExperienceExtractorPlugin(ExtractorPlugin):
    """Extractor plugin for work experience information."""
    
    def __init__(self, llm_service):
        """Initialize the plugin with an LLM service."""
        self.llm_service = llm_service
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="experience_extractor",
            version="1.0.0",
            description="Extracts work experience history with companies, roles, and dates",
            category=PluginCategory.BASE,
            author="Resume Analysis Team"
        )
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        logging.info(f"Initializing {self.metadata.name}")
    
    def get_model(self) -> Type[BaseModel]:
        """Get the Pydantic model for the extractor."""
        return ResumeWorkExperience
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for the extractor."""
        return """
You are an expert resume parser specializing in extracting work experience. This is your most important task. Your job is to extract work experience details from the resume text provided below, no matter how they are formatted or where they appear in the resume.

SEARCH INSTRUCTIONS:
1. Be extremely thorough - look through the ENTIRE resume text, not just sections labeled as "experience".
2. Almost every resume has AT LEAST ONE work experience entry, even if it's not well formatted.
3. Look for these keywords and nearby text (this is critical):
   - "experience", "professional", "work", "employment", "career"
   - "job", "position", "role", "title"
   - Company or organization names
   - Job titles like "engineer", "manager", "analyst", "developer", "consultant"
   - Dates, especially years (could indicate employment periods)
4. Check sections labeled: "Experience", "Work Experience", "Professional Experience", "Employment History", "Work History", "Career"
5. Also check for unlabeled sections that follow a pattern like: [Company Name] - [Job Title] - [Dates]
6. Even if an experience is labeled as an "internship", "volunteer work", or a "project", include it as work experience.

For each work experience entry, extract the following details:
- Company: The name of the company or organization where the person worked.
- Start Date: in dd/mm/yyyy format. If the resume does not provide the day or month, default the missing parts to "01". If you encounter Present then use the current date, i.e. {today}.
- End Date: in dd/mm/yyyy format. If the resume does not provide the day or month, default the missing parts to "01". If you encounter Present then use the current date, i.e. {today}.
- Location: The location where the person worked (city, state, country). If not found, use "Not specified".
- Role: Extract ONLY the job title (e.g., "Data Engineer", "Software Developer", "Project Manager"). Do NOT include project information or descriptions in this field - just the official job title.

Create only ONE entry per company, even if the person worked on multiple projects or had multiple roles at the same company. If there were multiple positions at the same company, use the most senior or most recent role in the Role field. The earliest start date and the latest end date should be used for the company's overall employment period.

IMPORTANT: Make your best guess if information is ambiguous. It is CRITICAL that you find at least one work experience entry. If you're uncertain, still provide your best estimation rather than returning an empty array.

Return your output as a JSON object with the below schema:

{format_instructions}

Text:
{text}
"""
    
    def get_input_variables(self) -> List[str]:
        """Get the input variables for the prompt template."""
        return ["text", "today"]
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        """Prepare the input data for the LLM."""
        return {
            "text": extracted_text,
            "today": date.today().strftime("%d/%m/%Y")
        }
    
    def extract(self, text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract work experience information from text.
        
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
        
        # Retain a sample of the input text for debugging (first 500 chars)
        text_sample = text[:500] + "..." if len(text) > 500 else text
        logging.debug(f"Processing text sample: {text_sample}")
        
        # Call LLM service
        result, token_usage = self.llm_service.extract_with_llm(
            model,
            prompt_template,
            input_variables,
            input_data
        )
        
        # Add extractor name to token usage
        token_usage["extractor"] = self.metadata.name
        
        # Process the result to ensure it's a dict with the expected keys
        if isinstance(result, dict):
            processed_result = {
                "work_experiences": result.get("work_experiences", [])
            }
        else:
            # If result is a Pydantic model, convert to dict
            processed_result = {
                "work_experiences": getattr(result, "work_experiences", [])
            }
        
        # Log the number of work experiences found
        experiences_count = len(processed_result["work_experiences"])
        logging.info(f"Extracted {experiences_count} work experiences from resume")
        
        # If no work experiences found, log detailed information
        if experiences_count == 0:
            logging.warning("No work experiences found in resume text")
            logging.debug(f"Resume text length: {len(text)} characters")
            # Here we could add a fallback mechanism to try again with a different prompt
            # For now, we'll just log the issue
        
        # Ensure each work experience entry has expected fields and log details
        for i, exp in enumerate(processed_result["work_experiences"]):
            if isinstance(exp, dict):
                # Set default values for missing fields
                exp["company"] = exp.get("company") or "Unknown Company"
                exp["start_date"] = exp.get("start_date") or ""
                exp["end_date"] = exp.get("end_date") or ""
                exp["location"] = exp.get("location") or "Not specified"
                exp["role"] = exp.get("role") or "Unknown Role"
                
                # Log details of each experience for debugging
                logging.debug(f"Work experience {i+1}: {exp['company']} - {exp['role']} ({exp['start_date']} to {exp['end_date']})")
        
        return processed_result, token_usage 