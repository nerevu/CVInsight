import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API keys - raise error if key is missing
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please create a .env file based on .env.example")

# LLM Models
DEFAULT_LLM_MODEL = os.environ.get("DEFAULT_LLM_MODEL", "gemini-2.0-flash")

# Date formats
DATE_FORMAT = "%d/%m/%Y"

# PDF processing configuration
PDF_EXTRACTION_METHOD = "PyPDF2"  # Options: 'PyPDF2', 'custom'

# File validation
MAX_PDF_SIZE_MB = 10  # Maximum PDF file size in MB
ALLOWED_FILE_EXTENSIONS = ['.pdf', '.docx']  # Allowed file extensions

# Directory configuration
RESUME_DIR = os.environ.get("RESUME_DIR", "./Resumes")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./Results")

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = os.environ.get("LOG_FILE", "resume_analysis.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 