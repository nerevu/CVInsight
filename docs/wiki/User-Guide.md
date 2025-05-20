# User Guide

This guide will help you use the CVInsight package effectively to process and analyze resumes.

## Getting Started

CVInsight offers multiple ways to interact with the system:

1. **Python API**: Using the client interface in your code
2. **Functional API**: Direct function calls for specific operations
3. **Command-Line Interface**: Command-line tool for processing resumes

## Python API

### Client Interface

The `CVInsightClient` class provides a clean, object-oriented interface:

```python
from cvinsight import CVInsightClient

# Initialize with your API key
client = CVInsightClient(api_key="your_google_api_key")

# Extract all information
results = client.extract_all("path/to/resume.pdf")

# Print the results
print(f"Name: {results.get('name')}")
print(f"Email: {results.get('email')}")
print(f"Skills: {', '.join(results.get('skills', []))}")
```

### Specific Extraction Methods

The client offers methods for targeted extraction:

```python
# Extract just profile information
profile = client.extract_profile("path/to/resume.pdf")
print(f"Name: {profile.get('name')}")

# Extract just skills
skills = client.extract_skills("path/to/resume.pdf")
print(f"Skills: {', '.join(skills.get('skills', []))}")

# Extract education history
education = client.extract_education("path/to/resume.pdf")
for edu in education:
    print(f"Degree: {edu.get('degree')} at {edu.get('institution')}")

# Extract work experience
experience = client.extract_experience("path/to/resume.pdf")
for exp in experience:
    print(f"Role: {exp.get('role')} at {exp.get('company')}")

# Extract years of experience
yoe = client.extract_years_of_experience("path/to/resume.pdf")
print(f"Years of Experience: {yoe}")
```

### Plugin Management

The client also provides methods for working with plugins:

```python
# List all available plugins
plugins = client.list_all_plugins()
for plugin in plugins:
    print(f"Plugin: {plugin['name']} - {plugin['description']}")

# List plugins by category
analyzer_plugins = client.list_plugins_by_category("ANALYZER")
for plugin in analyzer_plugins:
    print(f"Analyzer Plugin: {plugin['name']}")

# Analyze with specific plugins
results = client.analyze_resume("path/to/resume.pdf", 
                            plugins=["profile_extractor", "skills_extractor"])
```

## Functional API

CVInsight also provides a functional API for direct use:

```python
from cvinsight import (
    extract_all,
    extract_profile,
    extract_education,
    extract_experience,
    extract_skills,
    extract_years_of_experience,
    analyze_resume,
    list_all_plugins,
    list_plugins_by_category
)

# Extract all information
results = extract_all("path/to/resume.pdf")

# Extract specific information
profile = extract_profile("path/to/resume.pdf")
skills = extract_skills("path/to/resume.pdf")
education = extract_education("path/to/resume.pdf")
experience = extract_experience("path/to/resume.pdf")
yoe = extract_years_of_experience("path/to/resume.pdf")

# List plugins
plugins = list_all_plugins()
analyzer_plugins = list_plugins_by_category("ANALYZER")
```

## Command-Line Interface

### Basic Usage

```bash
# Install the package
pip install cvinsight

# Process a resume
cvinsight --resume path/to/resume.pdf

# List available plugins
cvinsight --list-plugins
```

### CLI Options

```bash
# Process a single resume file
cvinsight --resume example.pdf

# Specify output directory
cvinsight --resume example.pdf --output ./results

# Use specific plugins
cvinsight --resume example.pdf --plugins profile_extractor,skills_extractor

# Output as JSON
cvinsight --resume example.pdf --json
```

## Output Formats

### Resume Analysis Results

The tool generates structured JSON output for each processed resume:

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

### Token Usage Reports

The system tracks and reports token usage for each processed resume:

```json
{
  "token_usage": {
    "total_tokens": 7695,
    "prompt_tokens": 7410,
    "completion_tokens": 285,
    "by_extractor": {
      "profile": {
        "total_tokens": 1445,
        "prompt_tokens": 1423,
        "completion_tokens": 22,
        "source": "plugin"
      },
      "skills": {
        "total_tokens": 1383,
        "prompt_tokens": 1304,
        "completion_tokens": 79,
        "source": "plugin"
      },
      "education": {
        "total_tokens": 1672,
        "prompt_tokens": 1624,
        "completion_tokens": 48,
        "source": "plugin"
      },
      "experience": {
        "total_tokens": 1704,
        "prompt_tokens": 1586,
        "completion_tokens": 118,
        "source": "plugin"
      },
      "yoe": {
        "total_tokens": 1491,
        "prompt_tokens": 1473,
        "completion_tokens": 18,
        "source": "plugin"
      }
    }
  }
}
```

## Advanced Features

### Token Usage Tracking

CVInsight automatically logs token usage information:

```python
# Enable token usage logging (enabled by default)
results = client.extract_all("path/to/resume.pdf", log_token_usage=True)

# Token usage logs are stored in the 'logs' directory
```

### Custom Plugins

You can create and use custom plugins with CVInsight:

```python
from cvinsight.base_plugins import ExtractorPlugin, PluginMetadata, PluginCategory
from pydantic import BaseModel, Field
from typing import Dict, Any, Type, List

# Define a custom plugin
class CustomPlugin(ExtractorPlugin):
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="custom_analyzer",
            version="1.0.0",
            description="Custom analysis plugin",
            category=PluginCategory.ANALYZER,
            author="Your Name"
        )
    
    def get_model(self) -> Type[BaseModel]:
        class CustomModel(BaseModel):
            custom_field: str = Field(description="Custom field")
        
        return CustomModel
    
    def get_prompt_template(self) -> str:
        return """
        Analyze the following resume text and provide custom analysis.
        {format_instructions}
        
        Text:
        {text}
        """
    
    def get_input_variables(self) -> List[str]:
        return ["text"]

# Register and use the custom plugin
custom_plugin = CustomPlugin()
client._plugin_manager.register_plugin(custom_plugin)
```

## Best Practices

1. **Resume Format**
   - Use PDF or DOCX format for best results
   - Ensure resumes are properly formatted and readable
   - Avoid scanned documents or images

2. **Performance**
   - Process one resume at a time for better accuracy
   - Monitor token usage to optimize costs
   - Use specific extractors when you only need certain information

3. **Error Handling**
   - Implement proper try/except blocks in your code
   - Check return values for expected fields
   - Verify API key validity

4. **Security**
   - Keep API keys secure
   - Don't hardcode API keys in your code
   - Use environment variables for sensitive information

## Troubleshooting

### Common Issues

1. **API Errors**
   - Check API key validity
   - Verify internet connection
   - Monitor API rate limits

2. **Processing Failures**
   - Check resume file format
   - Verify file permissions
   - Look for error messages in the response

3. **Token Usage Issues**
   - Monitor token usage reports
   - Check prompt templates
   - Verify API quota

### Getting Help

- Check the [FAQ & Troubleshooting](FAQ-and-Troubleshooting) page
- Review the [Examples & Tutorials](Examples-and-Tutorials)
- Open an issue on GitHub for bugs or feature requests 