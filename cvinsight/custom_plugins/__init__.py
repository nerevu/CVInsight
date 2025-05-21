"""Custom plugins for Resume Analysis."""

from typing import List

# Import all our custom plugin classes
from .relevant_yoe_extractor.relevant_yoe_extractor import RelevantYoEExtractorPlugin
from .education_stats_extractor.education_stats_extractor import EducationStatsExtractorPlugin  
from .work_stats_extractor.work_stats_extractor import WorkStatsExtractorPlugin
from .social_extractor.social_extractor import SocialExtractorPlugin

# Define the list of all custom plugins
__all__: List[str] = [
    "RelevantYoEExtractorPlugin",
    "EducationStatsExtractorPlugin",
    "WorkStatsExtractorPlugin", 
    "SocialExtractorPlugin",
]