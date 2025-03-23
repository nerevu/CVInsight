# Resume Analysis

A powerful tool for extracting and analyzing information from resumes using Large Language Models (LLMs).

## Overview

Resume Analysis is a Python-based application that helps streamline the resume review process by automatically extracting key information from PDF and DOCX resumes. The system uses Google's Gemini models to process and extract structured data from unstructured resume text.

## Features

- **Multiple Resume Formats**: Supports both PDF and DOCX resume file formats
- **Profile Extraction**: Extracts basic information like name, contact number, and email
- **Skills Analysis**: Identifies technical and soft skills from resumes
- **Education History**: Extracts educational qualifications with institution names, dates, and degrees
- **Work Experience**: Analyzes professional experience with company names, roles, and dates
- **Years of Experience**: Calculates total professional experience based on work history
- **Concurrent Processing**: Processes multiple aspects of resumes in parallel for efficiency
- **Structured Output**: Provides results in clean, structured JSON format
- **Token Usage Tracking**: Monitors and logs API token consumption for each resume processed
- **Separated Log Files**: Keeps resume outputs clean by storing token usage data in separate log files

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your API keys
6. Place resume files (PDF or DOCX format) in the `Resumes/` directory

## Usage

### Basic Usage

Run the main script to process all resumes in the Resumes directory:

```bash
python main.py
```

The processed results will be saved as JSON files in the configured output directory, and token usage information will be saved in the logs directory.

### Command-line Arguments

The application supports the following command-line arguments:

```bash
# Process a single resume file
python main.py --resume example.pdf

# Only display token usage report for a previously processed resume
python main.py --resume example.pdf --report-only

# Specify a custom directory for token usage logs
python main.py --log-dir ./custom_logs
```

### Token Usage Reports

The system tracks token usage for each resume processed and provides:

- A summary report in the console output
- Detailed JSON log files in the logs/token_usage directory
- Breakdown of token usage by extractor

### Configuration

You can configure the following options in the `.env` file:

- `GOOGLE_API_KEY`: Your Google API key for Gemini LLM
- `DEFAULT_LLM_MODEL`: Model name to use (default: gemini-2.0-flash)
- `RESUME_DIR`: Directory containing resume files (default: ./Resumes)
- `OUTPUT_DIR`: Directory for processed results (default: ./Results)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `LOG_FILE`: Path to log file

## Architecture

The application uses a modular, object-oriented architecture:

- **Resume Class**: Encapsulates all extracted resume information
- **ResumeProcessor**: Manages the processing of resume files
- **BaseExtractor**: Abstract base class for all specialized extractors
- **Specialized Extractors**: Extract specific information from resumes using LLMs
- **LLM Service**: Centralized service for interacting with language models

## Example Output

### Resume JSON Output

```json
{
  "name": "John Doe",
  "contact_number": "+1-123-456-7890",
  "email": "john.doe@example.com",
  "skills": [
    "Python",
    "Machine Learning",
    "Data Analysis",
    "SQL",
    "JavaScript"
  ],
  "educations": [
    {
      "institution": "University of Example",
      "start_date": "2015-09",
      "end_date": "2019-05",
      "location": "Boston, MA",
      "degree": "Bachelor of Science in Computer Science"
    }
  ],
  "work_experiences": [
    {
      "company": "Tech Company Inc.",
      "start_date": "2019-06",
      "end_date": "2023-03",
      "location": "San Francisco, CA",
      "role": "Software Engineer"
    }
  ],
  "YoE": "4 years"
}
```

### Token Usage Log Output

```json
{
  "resume_file": "John_Doe.pdf",
  "processed_at": "20250323_031534",
  "token_usage": {
    "total_tokens": 7695,
    "prompt_tokens": 7410,
    "completion_tokens": 285,
    "by_extractor": {
      "ProfileExtractor": {
        "total_tokens": 1445,
        "prompt_tokens": 1423,
        "completion_tokens": 22
      },
      "SkillsExtractor": {
        "total_tokens": 1383,
        "prompt_tokens": 1304,
        "completion_tokens": 79
      },
      "EducationExtractor": {
        "total_tokens": 1672,
        "prompt_tokens": 1624,
        "completion_tokens": 48
      },
      "ExperienceExtractor": {
        "total_tokens": 1704,
        "prompt_tokens": 1586,
        "completion_tokens": 118
      },
      "YoeExtractor": {
        "total_tokens": 1491,
        "prompt_tokens": 1473,
        "completion_tokens": 18
      }
    }
  }
}