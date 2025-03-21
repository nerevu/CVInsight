import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API keys
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyCgBrEbvU8Tp6bOsHEXQ5kmJ-4v4l0T3So")

# LLM Models
DEFAULT_LLM_MODEL = "gemini-2.0-flash"

# Date formats
DATE_FORMAT = "%d/%m/%Y"

# PDF processing configuration
PDF_EXTRACTION_METHOD = "PyPDF2"  # Options: 'PyPDF2', 'custom' 