# Resume Analysis

A powerful tool for extracting and analyzing information from resumes using Large Language Models (LLMs).

## Overview

Resume Analysis is a Python-based application that helps streamline the resume review process by automatically extracting key information from PDF resumes. The system uses Google's Gemini models to process and extract structured data from unstructured resume text.

## Features

- **Profile Extraction**: Extracts basic information like name, contact number, and email
- **Skills Analysis**: Identifies technical and soft skills from resumes
- **Education History**: Extracts educational qualifications with institution names, dates, and degrees
- **Work Experience**: Analyzes professional experience with company names, roles, and dates
- **Years of Experience**: Calculates total professional experience based on work history
- **Concurrent Processing**: Processes multiple aspects of resumes in parallel for efficiency
- **Structured Output**: Provides results in clean, structured JSON format

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your API keys
6. Place resume PDFs in the `Resumes/` directory

## Usage

Run the main script:

```bash
python main.py
```

The processed results will be saved as JSON files in the configured output directory.

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