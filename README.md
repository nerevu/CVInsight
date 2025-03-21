# Resume Analysis

A tool for extracting and analyzing information from resumes using LLMs.

## Project Structure

```
.
├── config.py               # Configuration settings and API keys
├── extractors/             # Package for specialized extractors
│   ├── __init__.py         # Package exports
│   ├── base_extractor.py   # Base class for all extractors
│   ├── profile_extractor.py # Profile information extractor
│   ├── skills_extractor.py # Skills extractor
│   ├── education_extractor.py # Education extractor
│   ├── experience_extractor.py # Work experience extractor
│   └── yoe_extractor.py    # Years of experience extractor
├── llm_service.py          # Centralized LLM service
├── main.py                 # Main application entry point
├── models.py               # Pydantic models
├── utils/                  # Utility functions
│   ├── __init__.py         # Package exports
│   └── common.py           # Common utility functions
├── requirements.txt        # Project dependencies
└── .env.example            # Example environment variables file
```

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

## Features

- Extracts profile information (name, contact, email)
- Extracts work experience details
- Extracts education history
- Analyzes years of experience
- Identifies skills 