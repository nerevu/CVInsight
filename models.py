from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import os

class Skills(BaseModel):
    skills: List[str] = Field(
        ...,
        description="A list of skills extracted from the resume text."
    )

class WorkDates(BaseModel):
    oldest_working_date: Optional[str] = Field(
        description="The oldest working date from the resume in dd/mm/yyyy format."
    )
    newest_working_date: Optional[str] = Field(
        description="The newest working date from the resume in dd/mm/yyyy format (the end date of last company)"
    )

class ProfileInfo(BaseModel):
    name: Optional[str]
    contact_number: Optional[str]
    email: Optional[str]

class WorkExperience(BaseModel):
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    role: Optional[str] = None

class ResumeWorkExperience(BaseModel):
    work_experiences: List[WorkExperience]

class Education(BaseModel):
    institution: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    degree: Optional[str] = None

class ResumeEducation(BaseModel):
    educations: List[Education]

class Resume(BaseModel):
    """A complete resume with all extracted information."""
    # Profile information
    name: Optional[str] = None
    contact_number: Optional[str] = None
    email: Optional[str] = None
    
    # Skills
    skills: List[str] = Field(default_factory=list)
    
    # Education
    educations: List[Education] = Field(default_factory=list)
    
    # Work Experience
    work_experiences: List[WorkExperience] = Field(default_factory=list)
    
    # Years of Experience
    YoE: Optional[str] = None
    
    # File information
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    
    # Token usage information
    token_usage: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_extractors_output(cls, profile: Dict[str, Any], skills: Dict[str, Any], 
                             education: Dict[str, Any], experience: Dict[str, Any], 
                             yoe: Dict[str, Any], file_path: str, 
                             token_usage: Optional[Dict[str, int]] = None) -> 'Resume':
        """
        Create a Resume instance from the output of various extractors.
        
        Args:
            profile: Output from the profile extractor
            skills: Output from the skills extractor
            education: Output from the education extractor
            experience: Output from the experience extractor
            yoe: Output from the years of experience extractor
            file_path: Path to the resume file
            token_usage: Dictionary containing token usage information
            
        Returns:
            A Resume instance with all the extracted information
        """
        file_name = os.path.basename(file_path)
        
        return cls(
            name=profile.get('name'),
            contact_number=profile.get('contact_number'),
            email=profile.get('email'),
            skills=skills.get('skills', []),
            educations=education.get('educations', []),
            work_experiences=experience.get('work_experiences', []),
            YoE=yoe.get('YoE'),
            file_path=file_path,
            file_name=file_name,
            token_usage=token_usage or {}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Resume instance to a dictionary.
        
        Returns:
            A dictionary representation of the Resume
        """
        return self.model_dump(exclude={'file_path', 'token_usage'}) 