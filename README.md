# CVInsight

A powerful tool for extracting and analyzing information from resumes using Large Language Models (LLMs) with a plugin-based architecture.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Resume Analysis is a Python-based application that helps streamline the resume review process by automatically extracting key information from PDF and DOCX resumes. The system uses Google's Gemini models to process and extract structured data from unstructured resume text through a flexible plugin architecture.

## Documentation

- **Wiki Pages**: For detailed documentation, examples, and guides, please visit our [Wiki](https://github.com/Gaurav-Kumar98/Resume-Analysis/wiki)
  - [Home](https://github.com/Gaurav-Kumar98/Resume-Analysis/wiki/Home)
  - [Installation and Setup](https://github.com/Gaurav-Kumar98/Resume-Analysis/wiki/Installation-and-Setup)
  - [User Guide](https://github.com/Gaurav-Kumar98/Resume-Analysis/wiki/User-Guide)
  - [Plugin System](https://github.com/Gaurav-Kumar98/Resume-Analysis/wiki/Plugin-System)
  - [Technical Documentation](https://github.com/Gaurav-Kumar98/Resume-Analysis/wiki/Technical-Documentation)
  - [Examples and Tutorials](https://github.com/Gaurav-Kumar98/Resume-Analysis/wiki/Examples-and-Tutorials)

- **Blog Post**: Learn more about the development process in the article [Building a Resume Parser with LLMs: A Step-by-Step Guide](https://www.linkedin.com/pulse/building-resume-parser-llms-step-by-step-guide-gaurav-kumar-82pqc)

## Features

- **Plugin-Based Architecture**: Easily extend functionality by adding new plugins
- **Multiple Resume Formats**: Supports both PDF and DOCX resume file formats
- **Profile Extraction**: Extracts basic information like name, contact number, and email
- **Skills Analysis**: Identifies skills from resumes
- **Education History**: Extracts educational qualifications with institution names, dates, and degrees
- **Work Experience**: Analyzes professional experience with company names, roles, and dates
- **Years of Experience**: Calculates total professional experience based on work history
- **Concurrent Processing**: Processes multiple aspects of resumes in parallel for efficiency
- **Structured Output**: Provides results in clean, structured JSON format
- **Token Usage Tracking**: Monitors and logs API token consumption for each resume processed
- **Separated Log Files**: Keeps resume outputs clean by storing token usage data in separate log files
- **Automatic Log Rotation**: Implements log rotation to keep log files manageable
- **Configurable Log Retention**: Automatically cleans up token usage logs after a configurable period

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

# Enable verbose logging
python main.py --verbose

# Clean up __pycache__ directories and compiled Python files
python main.py --cleanup
```

### Token Usage Reports

The system tracks token usage for each resume processed and provides:

- A summary report in the console output
- Detailed JSON log files in the logs/token_usage directory
- Breakdown of token usage by plugin

### Configuration Options

You can configure the following options in the `.env` file:

- `GOOGLE_API_KEY`: Your Google API key for Gemini LLM
- `DEFAULT_LLM_MODEL`: Model name to use (default: gemini-2.0-flash)
- `RESUME_DIR`: Directory containing resume files (default: ./Resumes)
- `OUTPUT_DIR`: Directory for processed results (default: ./Results)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `LOG_FILE`: Path to log file
- `TOKEN_LOG_RETENTION_DAYS`: Number of days to keep token usage logs (default: 7)
- `LOG_MAX_SIZE_MB`: Maximum size of log files before rotation in MB (default: 5)
- `LOG_BACKUP_COUNT`: Number of backup log files to keep (default: 3)
- `DEBUG`: Enable or disable debug mode (default: False)

## Plugin Architecture

The application uses a modular, plugin-based architecture:

- **Plugin Manager**: Discovers, loads, and manages plugins
- **Base Plugin**: Abstract base class for all plugins
- **Built-in Plugins**: Profile, Skills, Education, Experience, and YoE extractors
- **Custom Plugins**: Add your own plugins in the `custom_plugins` directory
- **Plugin Resume Processor**: Processes resumes using the loaded plugins
- **LLM Service**: Centralized service for interacting with language models

For detailed documentation about the plugin architecture and creating custom plugins, please refer to our [Plugin System Wiki Page](https://github.com/Gaurav-Kumar98/Resume-Analysis/wiki/Plugin-System).

### Creating Custom Plugins

You can create custom plugins by inheriting from the `BasePlugin` class and implementing the required methods:

1. Create a new Python file in the `custom_plugins` directory
2. Import the `BasePlugin` class from `base_plugins.base`
3. Create a class that inherits from `BasePlugin`
4. Implement the required abstract methods: `name`, `version`, `description`, `category`, `get_model`, `get_prompt_template`, and `process_output`
5. Add your plugin to the `__all__` list in `custom_plugins/__init__.py`

Check out the [Examples and Tutorials](https://github.com/Gaurav-Kumar98/Resume-Analysis/wiki/Examples-and-Tutorials) wiki page for more examples on how to create and use custom plugins.

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
      "ProfileExtractorPlugin": {
        "total_tokens": 1445,
        "prompt_tokens": 1423,
        "completion_tokens": 22
      },
      "SkillsExtractorPlugin": {
        "total_tokens": 1383,
        "prompt_tokens": 1304,
        "completion_tokens": 79
      },
      "EducationExtractorPlugin": {
        "total_tokens": 1672,
        "prompt_tokens": 1624,
        "completion_tokens": 48
      },
      "ExperienceExtractorPlugin": {
        "total_tokens": 1704,
        "prompt_tokens": 1586,
        "completion_tokens": 118
      },
      "YoeExtractorPlugin": {
        "total_tokens": 1491,
        "prompt_tokens": 1473,
        "completion_tokens": 18
      }
    }
  }
}
