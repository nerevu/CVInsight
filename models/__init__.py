# Models package

from models.resume_models import (
    ResumeProfile,
    ResumeSkills,
    Education,
    ResumeEducation,
    Experience,
    ResumeWorkExperience,
    WorkDates,
    JobTitleMatch,
    Resume,
    Skills
)

# Alias for backwards compatibility (old code that imports ProfileInfo from models)
ProfileInfo = ResumeProfile

# Import Skills from models.py for backwards compatibility
from models import Skills 