from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

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
    company: str
    start_date: str
    end_date: str  
    location: str
    role: str

class ResumeWorkExperience(BaseModel):
    work_experiences: List[WorkExperience]

class Education(BaseModel):
    institution: str
    start_date: str   
    end_date: str     
    location: str
    degree: str

class ResumeEducation(BaseModel):
    educations: List[Education] 