"""Custom plugins for Resume Analysis."""

from typing import List

# Import all our custom plugin classes
from .extended_analysis_extractor.extended_analysis_extractor import ExtendedAnalysisExtractorPlugin

# Define the list of all custom plugins
__all__: List[str] = [
    "ExtendedAnalysisExtractorPlugin",
]