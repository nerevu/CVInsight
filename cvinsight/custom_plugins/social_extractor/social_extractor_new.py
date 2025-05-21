from typing import Dict, Any, Type, List, Optional
import re
from pydantic import BaseModel, Field, validator

from cvinsight.plugins.base import ExtractorPlugin, PluginMetadata, PluginCategory

class SocialProfiles(BaseModel):
    """Social media profiles and contact information."""
    phone_number: Optional[str] = Field(None, description="Contact phone number, formatted as 1-234-567-8901 for US numbers, or kept as is for international.")
    email: Optional[str] = Field(None, description="Contact email address.")
    linkedin_url: Optional[str] = Field(None, description="URL of the LinkedIn profile.")
    github_url: Optional[str] = Field(None, description="URL of the GitHub profile.")
    twitter_url: Optional[str] = Field(None, description="URL of the Twitter (X) profile.")
    facebook_url: Optional[str] = Field(None, description="URL of the Facebook profile.")
    instagram_url: Optional[str] = Field(None, description="URL of the Instagram profile.")
    stackoverflow_url: Optional[str] = Field(None, description="URL of the Stack Overflow profile.")
    personal_website_url: Optional[str] = Field(None, description="URL of a personal website or blog.")
    other_links: List[str] = Field(default_factory=list, description="Any other relevant social or professional links.")

    @validator('phone_number', pre=True)
    def format_phone_number(cls, v):
        if v is None:
            return None
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(v))
        
        # US number formatting
        if len(digits) == 11 and digits.startswith('1'):
            return f"1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
        elif len(digits) == 10 and (digits.startswith('2') or digits.startswith('3') or 
                                    digits.startswith('4') or digits.startswith('5') or 
                                    digits.startswith('6') or digits.startswith('7') or 
                                    digits.startswith('8') or digits.startswith('9')):
            return f"1-{digits[0:3]}-{digits[3:6]}-{digits[6:]}"
        
        # If not a standard US number, return as is
        return v

class SocialExtractorPlugin(ExtractorPlugin):
    """Plugin to extract social media profiles, contact details, and website links."""

    def __init__(self, llm_service=None):
        self.llm_service = llm_service

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="social_extractor",
            version="1.0.0",
            description="Extracts social media links (LinkedIn, GitHub, Twitter, etc.), websites, and formats phone numbers.",
            category=PluginCategory.CUSTOM,
            author="AI Assistant"
        )

    def initialize(self) -> None:
        pass

    def get_model(self) -> Type[BaseModel]:
        return SocialProfiles

    def get_prompt_template(self) -> str:
        return """
        From the resume text provided below, extract the following information:
        - Contact phone number. If found, please try to format it as 1-XXX-XXX-XXXX for US numbers.
          If it appears to be an international number, leave it in its original format.
        - Email address.
        - LinkedIn profile URL.
        - GitHub profile URL.
        - Twitter (or X) profile URL.
        - Facebook profile URL.
        - Instagram profile URL.
        - Stack Overflow profile URL.
        - Personal website or blog URL.
        - Any other relevant social or professional links.

        If a piece of information is not found, please omit it or leave it as null.

        Resume Text:
        {text}

        {format_instructions}
        """

    def get_input_variables(self) -> List[str]:
        return ["text"]

    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        return {"text": extracted_text}

    def process_output(self, result: Any) -> Dict[str, Any]:
        if isinstance(result, SocialProfiles):
            # The Pydantic validator for phone_number should handle formatting
            # You can add more processing here if needed
            return result.model_dump()
        return result
