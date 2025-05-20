# Examples & Tutorials

This page provides practical examples and tutorials for using the CVInsight package.

## Basic Usage Examples

### 1. Using the Client Interface

```python
from cvinsight import CVInsightClient

# Initialize the client (with your API key)
client = CVInsightClient(api_key="your_google_api_key")

# Process a single resume and get all information
results = client.extract_all("path/to/resume.pdf")

# Access the extracted information
print(f"Name: {results.get('name')}")
print(f"Email: {results.get('email')}")
print(f"Skills: {', '.join(results.get('skills', []))}")

# Extract specific information only
profile = client.extract_profile("path/to/resume.pdf")
education = client.extract_education("path/to/resume.pdf")
experience = client.extract_experience("path/to/resume.pdf")
skills = client.extract_skills("path/to/resume.pdf")
years_of_experience = client.extract_years_of_experience("path/to/resume.pdf")
```

### 2. Using the Functional API

```python
from cvinsight import extract_all, extract_profile, extract_skills

# Extract all information at once
results = extract_all("path/to/resume.pdf")

# Extract specific information
profile = extract_profile("path/to/resume.pdf")
skills = extract_skills("path/to/resume.pdf")

# Print the results
print(f"Name: {profile.get('name')}")
print(f"Email: {profile.get('email')}")
print(f"Skills: {', '.join(skills.get('skills', []))}")
```

### 3. Command-Line Interface

```bash
# Install the package
pip install cvinsight

# Process a resume and display results in the terminal
cvinsight --resume path/to/resume.pdf

# Output results as JSON
cvinsight --resume path/to/resume.pdf --json

# Save results to a specific directory
cvinsight --resume path/to/resume.pdf --output ./results

# List available plugins
cvinsight --list-plugins

# Use specific plugins only
cvinsight --resume path/to/resume.pdf --plugins profile_extractor,skills_extractor
```

## Processing Multiple Resumes

### 1. Process a Directory of Resumes

```python
import os
from cvinsight import CVInsightClient

# Initialize the client
client = CVInsightClient()

# Path to directory containing resumes
resume_dir = "./Resumes"
output_dir = "./Results"
os.makedirs(output_dir, exist_ok=True)

# Get all PDF and DOCX files
resume_files = []
for file in os.listdir(resume_dir):
    if file.lower().endswith(('.pdf', '.docx')):
        resume_files.append(os.path.join(resume_dir, file))

# Process each resume
for resume_file in resume_files:
    try:
        print(f"Processing {resume_file}...")
        results = client.extract_all(resume_file)
        
        # Save results to JSON file
        base_name = os.path.splitext(os.path.basename(resume_file))[0]
        output_file = os.path.join(output_dir, f"{base_name}.json")
        
        import json
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"Saved results to {output_file}")
    except Exception as e:
        print(f"Error processing {resume_file}: {e}")
```

## Custom Plugin Development

### 1. Creating a Simple Custom Plugin

```python
from cvinsight.base_plugins import ExtractorPlugin, PluginMetadata, PluginCategory
from pydantic import BaseModel, Field
from typing import Dict, Any, Type, List, Optional

# Define the data model for certifications
class Certification(BaseModel):
    """Model for certification information."""
    name: str = Field(..., description="Name of the certification")
    organization: str = Field(..., description="Organization that issued the certification")
    date_obtained: Optional[str] = Field(None, description="Date when certification was obtained")
    expiration_date: Optional[str] = Field(None, description="Expiration date if applicable")

class Certifications(BaseModel):
    """Model for certifications list."""
    certifications: List[Certification] = Field(default_factory=list, description="List of certifications")

# Define the certification extractor plugin
class CertificationExtractorPlugin(ExtractorPlugin):
    """Plugin to extract certifications from resumes."""
    
    def __init__(self, llm_service=None):
        """Initialize the plugin."""
        self.llm_service = llm_service
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="certification_extractor",
            version="1.0.0",
            description="Extracts certification information from resumes",
            category=PluginCategory.EXTRACTOR,
            author="Your Name"
        )
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass
    
    def get_model(self) -> Type[BaseModel]:
        """Get the Pydantic model for certifications."""
        return Certifications
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for extracting certifications."""
        return """
        Extract certification information from the resume text.
        For each certification, include name, issuing organization, date obtained, and expiration date.
        
        {format_instructions}
        
        Text:
        {text}
        """
    
    def get_input_variables(self) -> List[str]:
        """Get the input variables for the prompt template."""
        return ["text"]
```

### 2. Using a Custom Plugin

```python
from cvinsight import CVInsightClient
from custom_plugins import CertificationExtractorPlugin  # Import your custom plugin

# Initialize the client
client = CVInsightClient()

# Create and register the custom plugin
cert_plugin = CertificationExtractorPlugin()
client._plugin_manager.register_plugin(cert_plugin)

# Process a resume with the custom plugin
results = client.extract_all("path/to/resume.pdf")

# Access certification information
certifications = results.get("certification_extractor", {}).get("certifications", [])
for cert in certifications:
    print(f"Certification: {cert.get('name')}")
    print(f"  Organization: {cert.get('organization')}")
    print(f"  Obtained: {cert.get('date_obtained')}")
    print(f"  Expires: {cert.get('expiration_date')}")
```

## Advanced Examples

### 1. Job Matching Plugin

This example demonstrates how to create a plugin that matches a resume against a job description:

```python
from cvinsight.base_plugins import ExtractorPlugin, PluginMetadata, PluginCategory
from pydantic import BaseModel, Field
from typing import Dict, Any, Type, List

class JobMatch(BaseModel):
    """Model for job matching results."""
    match_percentage: int = Field(..., description="Match percentage from 0-100")
    matching_skills: List[str] = Field(default_factory=list, description="Skills that match job requirements")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills missing from resume")
    recommendation: str = Field(..., description="Overall recommendation")

class JobMatchPlugin(ExtractorPlugin):
    """Plugin to match resumes against job descriptions."""
    
    def __init__(self, job_description: str, llm_service=None):
        """Initialize with a job description."""
        self.job_description = job_description
        self.llm_service = llm_service
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="job_matcher",
            version="1.0.0",
            description="Matches resumes against job descriptions",
            category=PluginCategory.ANALYZER,
            author="Your Name"
        )
    
    def get_model(self) -> Type[BaseModel]:
        """Get the Pydantic model for job matching."""
        return JobMatch
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for job matching."""
        return """
        Evaluate how well the candidate's resume matches the job description below.
        
        JOB DESCRIPTION:
        {job_description}
        
        RESUME:
        {text}
        
        Provide a match percentage (0-100), list matching skills, list missing required skills,
        and give an overall recommendation.
        
        {format_instructions}
        """
    
    def get_input_variables(self) -> List[str]:
        """Get the input variables for the prompt template."""
        return ["text", "job_description"]
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        """Prepare input data for the prompt template."""
        return {
            "text": extracted_text,
            "job_description": self.job_description
        }
```

### 2. Using the Job Matching Plugin

```python
from cvinsight import CVInsightClient
from custom_plugins import JobMatchPlugin

# Job description
job_description = """
We are looking for a Python Developer with the following skills:
- 3+ years experience with Python
- Experience with Django or FastAPI
- Familiarity with SQL databases (PostgreSQL preferred)
- Experience with cloud platforms (AWS, Azure, or GCP)
- Good understanding of REST APIs
- Knowledge of CI/CD pipelines
"""

# Initialize the client
client = CVInsightClient()

# Create and register the job matching plugin
job_matcher = JobMatchPlugin(job_description)
client._plugin_manager.register_plugin(job_matcher)

# Process a resume with the job matcher
results = client.extract_all("path/to/resume.pdf")

# Access job matching results
job_match = results.get("job_matcher", {})
print(f"Match percentage: {job_match.get('match_percentage')}%")
print("Matching skills:")
for skill in job_match.get('matching_skills', []):
    print(f"- {skill}")
print("Missing skills:")
for skill in job_match.get('missing_skills', []):
    print(f"- {skill}")
print(f"Recommendation: {job_match.get('recommendation')}")
```

### 3. Token Usage Analysis

This example shows how to analyze and optimize token usage:

```python
import json
import os
from cvinsight import CVInsightClient

# Initialize the client
client = CVInsightClient()

# Process a resume
results = client.extract_all("path/to/resume.pdf", log_token_usage=True)

# Find the most recent token usage log
logs_dir = "./logs"
token_logs = [f for f in os.listdir(logs_dir) if f.endswith("_token_usage_") and f.endswith(".json")]
token_logs.sort(reverse=True)  # Sort by most recent

if token_logs:
    latest_log = os.path.join(logs_dir, token_logs[0])
    with open(latest_log, 'r') as f:
        token_data = json.load(f)
        
    # Analyze token usage
    total_tokens = token_data.get("token_usage", {}).get("total_tokens", 0)
    prompt_tokens = token_data.get("token_usage", {}).get("prompt_tokens", 0)
    completion_tokens = token_data.get("token_usage", {}).get("completion_tokens", 0)
    
    print(f"Total tokens: {total_tokens}")
    print(f"Prompt tokens: {prompt_tokens} ({prompt_tokens/total_tokens:.1%})")
    print(f"Completion tokens: {completion_tokens} ({completion_tokens/total_tokens:.1%})")
    
    # Analyze by extractor
    print("\nToken usage by extractor:")
    by_extractor = token_data.get("token_usage", {}).get("by_extractor", {})
    for extractor, usage in by_extractor.items():
        print(f"  {extractor}: {usage.get('total_tokens', 0)} tokens")
```

## Best Practices

1. **Error Handling**: Always implement proper error handling when using the CVInsight API.
2. **API Key Management**: Use environment variables for API keys rather than hardcoding them.
3. **Token Optimization**: Use specific extractors when you only need certain information.
4. **Resume Format**: Ensure resumes are in a standard format (PDF or DOCX) for best results.
5. **Testing**: Test your custom plugins with a variety of resume formats and structures. 