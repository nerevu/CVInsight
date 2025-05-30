# CVInsight

AI-powered resume parsing and analysis using OpenAI models.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

CVInsight is a production-ready Python package that streamlines the resume review process by automatically extracting key information from PDF and DOCX resumes. The system uses OpenAI GPT models to process and extract structured data from unstructured resume text through an optimized plugin architecture.

## Key Features

- **🚀 High Performance**: 75% faster processing with unified extractor architecture
- **📊 Comprehensive Analysis**: Extracts 21+ structured fields including experience relevance scoring
- **⚡ Smart Processing**: Parallel processing with intelligent dependency management
- **📝 Multiple Formats**: Supports PDF and DOCX resume formats
- **🎯 Job Matching**: Context-aware relevance scoring against job descriptions
- **🔧 Production Ready**: Robust error handling, logging, and comprehensive test coverage

## Performance Highlights

### ⚡ Unified Extractor Architecture
- **75% Performance Improvement**: Reduced processing time from ~102s to ~25s per resume
- **Single LLM Call**: Consolidated 4 separate extractors into one unified analysis
- **Cost Efficient**: Significant reduction in API token usage
- **21 Analysis Fields**: Comprehensive candidate assessment in one call

### 🎯 Advanced Features
- **Job-Specific Relevance**: Dynamic experience relevance scoring based on job descriptions
- **Education Analysis**: Intelligent degree mapping and years calculation
- **Experience Scoring**: Separate tracking of total vs. relevant work experience
- **Contact Extraction**: Comprehensive contact information parsing including social profiles
- **Parallel Processing**: Optimized multi-threaded resume processing

### 🧪 Production Quality
- **100% Test Coverage**: 51/51 tests passing across unit, integration, and functional tests
- **Error Recovery**: Robust error handling with detailed logging
- **Plugin System**: Extensible architecture for custom extractors
- **Documentation**: Comprehensive examples and API documentation

## Usage

```bash
# Process all resumes in the Resumes directory
python run_resumes.py --all

# Process a limited number of resumes (e.g., 5)
python run_resumes.py --limit 5
```

## Jupyter Notebook Integration

CVInsight can be easily integrated into Jupyter notebooks for interactive resume analysis:

```python
# Import CVInsight notebook utilities
from cvinsight.notebook_utils import initialize_client, parse_single_resume, parse_many_resumes, find_resumes

# Initialize client with API key
client = initialize_client(api_key="your_api_key_here", provider="openai")

# Find and parse resumes
resume_paths = find_resumes("path/to/resumes")
resumes_df = parse_many_resumes(client, resume_paths, parallel=True)

# Work with the results DataFrame
print(f"Successfully parsed: {(resumes_df['parsing_status'] == 'success').sum()}")
```

For detailed instructions on integrating CVInsight with Jupyter notebooks, see [Notebook Integration Guide](docs/notebook_integration.md).

Example notebooks are provided in the `examples` directory:
- [CVInsight Demo Notebook](examples/cvinsight_demo.ipynb) - Comprehensive demonstration
- [Target Notebook Integration](examples/target_notebook_integration.ipynb) - Integration example

## Performance Metrics

**Current Optimized Architecture Performance**:
- **Plugin Architecture**: 5 base plugins + 1 unified custom plugin (vs. previous 5 base + 4 custom)
- **API Call Reduction**: 75% fewer LLM calls for custom analysis
- **Processing Efficiency**: Single comprehensive analysis vs. multiple separate analyses
- **Token Usage**: Significantly reduced through unified prompting strategy

**Latest Performance Results**:
- 100% success rate (21/21 resumes processed)
- Average processing time: Optimized through unified plugin architecture
- Comprehensive analysis: 21 advanced fields extracted per resume
- Cost Efficiency: Reduced token consumption through consolidated LLM calls

**Plugin Performance**:
- **Base Plugins**: Essential data extraction (profile, skills, education, experience, YoE)
- **Extended Analysis Plugin**: Unified comprehensive analysis replacing 4 individual extractors
- **Parallel Processing**: Base plugins run in parallel for maximum efficiency
- **Dependency Management**: Sequential execution where data dependencies exist

## Output

The script generates a single CSV file containing all extracted information from the resumes at: `Results/resume_analysis_results.csv`

## Installation

```bash
pip install cvinsight
```

## Quick Start

### Using the Client Interface (Recommended)

```python
from cvinsight import CVInsightClient

# Initialize with your API key
client = CVInsightClient(api_key="YOUR_GEMINI_API_KEY")

# Extract all information from a resume (token usage logged to separate file)
result = client.extract_all("path/to/resume.pdf")
print(result)  # Clean dictionary output without token usage data

# Or extract specific components (all return dictionaries)
profile = client.extract_profile("path/to/resume.pdf")
education = client.extract_education("path/to/resume.pdf")
experience = client.extract_experience("path/to/resume.pdf")
skills = client.extract_skills("path/to/resume.pdf")
yoe = client.extract_years_of_experience("path/to/resume.pdf")
```

### Using the API (Alternative)

```python
import cvinsight

# Configure the API with your credentials
cvinsight.api.configure(api_key="YOUR_GEMINI_API_KEY")

# Extract information from a resume (token usage logged to separate file)
result = cvinsight.extract_all("path/to/resume.pdf")
profile = cvinsight.extract_profile("path/to/resume.pdf")
education = cvinsight.extract_education("path/to/resume.pdf")
```

### Complete Example

```python
import os
import json
from dotenv import load_dotenv
from cvinsight import CVInsightClient

# Load API key from .env file if available
load_dotenv()

# Get API key from environment or prompt
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    api_key = input("Enter your Gemini API key: ")

# Initialize client with API key
client = CVInsightClient(api_key=api_key)
resume_path = "path/to/resume.pdf"

# Extract and print years of experience
print("Years of experience:", client.extract_years_of_experience(resume_path))

# Extract and print skills as formatted JSON
skills = client.extract_skills(resume_path)
print("\nSkills:")
print(json.dumps(skills, indent=2))

# Extract all information (token usage logged separately to logs/ directory)
result = client.extract_all(resume_path, log_token_usage=True)
print("\nFull resume information:")
print(json.dumps(result, indent=2))
```

## Configuration

### API Key

You can set the API key in multiple ways:

1.  **Directly in Code (as shown in Quick Start) (Not recommended)**
2.  **Environment Variable:**
    ```bash
    # In your shell
    export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```
3.  **`.env` File:** Create a `.env` file in your project directory (Recommended):
    ```
    GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
    ```

### Other Configuration Options

You can configure the following options in the `.env` file (primarily for development and advanced usage):

- `DEFAULT_LLM_MODEL`: Model name to use (default: gemini-2.0-flash)
- `RESUME_DIR`: Directory containing resume files (default: ./Resumes)
- `OUTPUT_DIR`: Directory for processed results (default: ./Results)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)
- `LOG_FILE`: Path to log file
- `TOKEN_LOG_RETENTION_DAYS`: Number of days to keep token usage logs (default: 7)
- `LOG_MAX_SIZE_MB`: Maximum size of log files before rotation in MB (default: 5)
- `LOG_BACKUP_COUNT`: Number of backup log files to keep (default: 3)
- `DEBUG`: Enable or disable debug mode (default: False)


## Command Line Usage

```bash
# Process a resume with all plugins
cvinsight --resume path/to/resume.pdf

# List available plugins
cvinsight --list-plugins

# Process with specific plugins
cvinsight --resume path/to/resume.pdf --plugins profile_extractor,skills_extractor

# Output as JSON
cvinsight --resume path/to/resume.pdf --json

# Save to specific directory
cvinsight --resume path/to/resume.pdf --output ./results
```

For development and advanced usage, `main.py` supports additional arguments:

```bash
# Process a single resume file (using main.py directly)
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

Example CLI output:
```
Resume Analysis Results:
Name: JOHN DOE
Email: john.doe@example.com
Skills: Python, SQL, Data Analysis, Machine Learning...

Education:
- Bachelor of Science in Computer Science at Example University

Experience:
- Software Engineer at Tech Company
Years of Experience: 5 Years
```

## Token Usage Logging

By default, token usage information is logged to separate files to keep the output data clean.

```python
# Enable token usage logging (default)
result = client.extract_all("resume.pdf", log_token_usage=True)

# Disable token usage logging if needed
result = client.extract_all("resume.pdf", log_token_usage=False)
```

Token usage logs are saved to the `logs/` directory with filenames that include the resume name and timestamp:
```
logs/token_usage/resume_name_token_usage_YYYYMMDD_HHMMSS.json
```

The system tracks token usage for each resume processed and provides:
- A summary report in the console output (when using `main.py`)
- Detailed JSON log files in the `logs/token_usage` directory
- Breakdown of token usage by plugin/extractor

### Token Usage Log Example

```json
{
  "resume_file": "John_Doe.pdf",
  "processed_at": "20250323_031534",
  "token_usage": {
    "total_tokens": 7695,
    "prompt_tokens": 7410,
    "completion_tokens": 285,
    "by_extractor": {
      "profile": {
        "total_tokens": 1445,
        "prompt_tokens": 1423,
        "completion_tokens": 22,
        "source": "message_usage_metadata" // Or "plugins" depending on context
      },
      "skills": {
        "total_tokens": 1383,
        "prompt_tokens": 1304,
        "completion_tokens": 79,
        "source": "message_usage_metadata"
      },
      "education": {
        "total_tokens": 1672,
        "prompt_tokens": 1624,
        "completion_tokens": 48,
        "source": "message_usage_metadata"
      },
      "experience": {
        "total_tokens": 1704,
        "prompt_tokens": 1586,
        "completion_tokens": 118,
        "source": "message_usage_metadata"
      },
      "yoe": {
        "total_tokens": 1491, // Example, actual could be 0 if calculated
        "prompt_tokens": 1473,
        "completion_tokens": 18,
        "source": "message_usage_metadata" // Or "calculated"
      }
    },
    "source": "plugins" // Or another top-level source
  }
}
```

## Dictionary Output

All methods in both the client and API interfaces return clean dictionaries or lists of dictionaries, making it easy to work with the extracted data and convert it to JSON:

```python
# Extract skills as dictionary
skills = client.extract_skills("resume.pdf")
print(skills)
# Output: {'skills': ['Python', 'Machine Learning', 'Data Analysis', ...]}

# Extract education as list of dictionaries
education = client.extract_education("resume.pdf")
print(education)
# Output: [{'degree': 'Bachelor of Science...', 'institution': 'University...', ...}]
```

## Example Output

### Complete Resume JSON Output

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
  "YoE": "4 years",
  "file_name": "john_doe.pdf"
}
```

### Skills Output

```json
{
  "skills": [
    "Python",
    "Machine Learning",
    "Data Analysis",
    "SQL",
    "JavaScript"
  ]
}
```

### Education Output

```json
[
  {
    "institution": "University of Example",
    "start_date": "2015-09",
    "end_date": "2019-05",
    "location": "Boston, MA",
    "degree": "Bachelor of Science in Computer Science"
  }
]
```

## Plugin Architecture

The application uses a modular, plugin-based architecture:

- **Plugin Manager**: Discovers, loads, and manages plugins
- **Base Plugin**: Abstract base class for all plugins  
- **Base Plugins (5)**: Core extractors for fundamental resume data
  - `profile_extractor`: Name, email, contact information
  - `skills_extractor`: Technical and soft skills
  - `education_extractor`: Educational background
  - `experience_extractor`: Work experience history
  - `yoe_extractor`: Years of experience calculation
- **Custom Plugins (1)**: Advanced analysis and insights
  - `extended_analysis_extractor`: Unified comprehensive analysis
- **Plugin Resume Processor**: Processes resumes using the loaded plugins
- **LLM Service**: Centralized service for interacting with language models

For detailed documentation about the plugin architecture and creating custom plugins, please refer to our [Plugin System Wiki Page](https://github.com/Gaurav-Kumar98/CVInsight/wiki/Plugin-System).

### Performance Benefits

**Current Architecture (6 Total Plugins)**:
- **5 Base Plugins**: Essential resume data extraction
- **1 Unified Custom Plugin**: Replaces 4 individual custom extractors
- **75% Reduction** in custom plugin API calls (from 4 calls to 1 call)
- **Faster Processing**: Single comprehensive analysis vs multiple separate analyses
- **Lower Costs**: Reduced token usage through unified prompting
- **Simpler Maintenance**: One plugin instead of four to maintain

### Custom Plugin: Extended Analysis Extractor

**Purpose**: A comprehensive unified plugin that combines all custom extraction capabilities into a single, high-performance analysis tool.

**Combined Fields Extracted** (21 total fields):

**Relevant Years of Experience** (4 fields):
- `all_wyoe`: Total years of ALL work experience
- `all_relevant_wyoe`: Years of RELEVANT work experience based on job description
- `all_eyoe`: Total years of ALL education experience  
- `relevant_eyoe`: Years of RELEVANT education experience based on job description

**Education Statistics** (4 fields):
- `highest_degree`: The highest academic degree obtained or being pursued
- `highest_degree_status`: Completion status - "completed", "pursuing", or "unknown"
- `highest_degree_major`: Field of study for the highest degree
- `highest_degree_school_prestige`: Institution prestige level - "low", "medium", or "high"

**Work Statistics** (3 fields):
- `highest_seniority_level`: Highest career level achieved (junior, mid-level, senior, lead, manager, director, executive, intern)
- `primary_position_title`: Most common or highest-ranking job title representing the candidate's primary role
- `average_tenure_at_company_years`: Average duration spent at each company (not individual roles)

**Social Profiles & Contact Information** (10 fields):
- `phone_number`: Contact phone number (formatted as 1-234-567-8901 for US numbers)
- `email`: Primary email address
- `linkedin_url`: LinkedIn profile URL
- `github_url`: GitHub profile URL
- `twitter_url`: Twitter/X profile URL
- `facebook_url`: Facebook profile URL
- `instagram_url`: Instagram profile URL
- `stackoverflow_url`: Stack Overflow profile URL
- `personal_website_url`: Personal website or blog URL
- `other_links`: Array of any other relevant social or professional links

**Key Features**:
- **Performance Optimized**: Single LLM call replaces 4 separate calls (75% reduction in API usage)
- **Intelligent Analysis**: Job description matching for relevance calculation
- **Degree Mapping**: Automatic degree-to-years mapping (PhD: 8 years, Master's: 6 years, Bachelor's: 4 years, etc.)
- **Contact Formatting**: Automatic US phone number formatting
- **Comprehensive Coverage**: All-in-one solution for resume analysis

### Sample Output Structure

The unified plugin contributes all fields to the final output with the plugin name as a prefix:

```csv
extended_analysis_extractor_all_wyoe,extended_analysis_extractor_all_relevant_wyoe,extended_analysis_extractor_highest_degree,extended_analysis_extractor_highest_degree_status,extended_analysis_extractor_highest_seniority_level,extended_analysis_extractor_linkedin_url,extended_analysis_extractor_email,extended_analysis_extractor_phone_number
3.3,2.8,Master of Science in Information Management,completed,senior,https://linkedin.com/in/username,user@email.com,1-555-123-4567
```

**Field Naming Convention**: All unified plugin fields use the prefix `extended_analysis_extractor_` followed by the field name (e.g., `extended_analysis_extractor_all_wyoe`, `extended_analysis_extractor_highest_degree`).

### Architecture Comparison

**Before (4 Separate Custom Extractors)**:
```python
# 4 separate LLM API calls per resume
relevant_yoe_extractor.extract(...)      # Call 1
education_stats_extractor.extract(...)   # Call 2  
work_stats_extractor.extract(...)        # Call 3
social_extractor.extract(...)            # Call 4
```

**After (1 Unified Custom Extractor)**:
```python
# 1 comprehensive LLM API call per resume
extended_analysis_extractor.extract(...)  # Single call with all 21 fields
```

**Performance Benefits**:
- 75% reduction in custom plugin API calls
- Faster processing time
- Lower token usage and costs
- Simplified maintenance

### Creating Custom Plugins

You can create custom plugins by inheriting from the `ExtractorPlugin` base class and implementing the required methods:

1. Create a new Python file in the `custom_plugins` directory
2. Import the `ExtractorPlugin` class from `cvinsight.plugins.base`
3. Create a class that inherits from `ExtractorPlugin`
4. Implement the required abstract methods: `metadata`, `get_model`, `get_prompt_template`, `get_input_variables`, `prepare_input_data`, and `extract`
5. Add your plugin to the `__all__` list in `custom_plugins/__init__.py`

**Example Custom Plugin Structure**:
```python
from cvinsight.plugins.base import ExtractorPlugin, PluginMetadata, PluginCategory
from pydantic import BaseModel

class MyCustomPlugin(ExtractorPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_custom_plugin",
            version="1.0.0",
            description="Custom analysis plugin",
            category=PluginCategory.CUSTOM,
            author="Your Name"
        )
    
    def get_model(self):
        # Return your Pydantic model
        pass
    
    def extract(self, text: str, additional_params=None):
        # Implement extraction logic
        pass
```

**Current Plugin Architecture**:
- **Base Plugins (5)**: Essential resume data extraction
- **Custom Plugins (1)**: Advanced unified analysis
- **Plugin Registration**: Automatic discovery and loading
- **Dependency Management**: Sequential execution for dependent plugins

Check out the [Examples and Tutorials](https://github.com/Gaurav-Kumar98/CVInsight/wiki/Examples-and-Tutorials) wiki page for more examples on how to create and use custom plugins.


## Setup (for Development)

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your API keys
6. Place resume files (PDF or DOCX format) in the `Resumes/` directory (or configure `RESUME_DIR` in `.env`)

## Documentation

- **Wiki Pages**: For detailed documentation, examples, and guides, please visit our [Wiki](https://github.com/Gaurav-Kumar98/CVInsight/wiki).
  - [Home](https://github.com/Gaurav-Kumar98/CVInsight/wiki/Home)
  - [Installation and Setup](https://github.com/Gaurav-Kumar98/CVInsight/wiki/Installation-and-Setup)
  - [User Guide](https://github.com/Gaurav-Kumar98/CVInsight/wiki/User-Guide)
  - [Plugin System](https://github.com/Gaurav-Kumar98/CVInsight/wiki/Plugin-System)
  - [Technical Documentation](https://github.com/Gaurav-Kumar98/CVInsight/wiki/Technical-Documentation)
  - [Examples and Tutorials](https://github.com/Gaurav-Kumar98/CVInsight/wiki/Examples-and-Tutorials)

- **Blog Post**: Learn more about the development process in the article [Building a Resume Parser with LLMs: A Step-by-Step Guide](https://www.linkedin.com/pulse/building-resume-parser-llms-step-by-step-guide-gaurav-kumar-82pqc)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.