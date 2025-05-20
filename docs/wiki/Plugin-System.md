# Plugin System

CVInsight uses a flexible plugin-based architecture that allows you to extend its functionality by creating custom plugins. This guide explains the plugin system and how to create your own plugins.

## Plugin Architecture Overview

### Core Components

1. **Plugin Manager**
   - Discovers and loads plugins
   - Manages plugin lifecycle
   - Provides methods for working with plugins

2. **Base Plugin**
   - Abstract base class for all plugins
   - Defines common interface
   - Provides utility methods

3. **Plugin Resume Processor**
   - Coordinates plugin execution
   - Manages concurrent processing
   - Handles results aggregation

### Built-in Plugins

The system includes several built-in plugins:

1. **Profile Extractor Plugin**
   - Extracts basic information
   - Name, contact details, email

2. **Skills Extractor Plugin**
   - Identifies skills from resume
   - Technical and soft skills

3. **Education Extractor Plugin**
   - Extracts educational history
   - Institutions, degrees, dates

4. **Experience Extractor Plugin**
   - Analyzes work experience
   - Companies, roles, dates

5. **YoE Extractor Plugin**
   - Calculates years of experience
   - Total professional experience

### Plugin Types
The system supports multiple types of plugins:
- **Extractor Plugins**: Implement the `ExtractorPlugin` interface to extract specific information from resumes
- **Custom Plugins**: Implement the `BasePlugin` interface for custom functionality
- **Processor Plugins**: Implement post-processing or analysis on extracted data

### Plugin Categories
Plugins are classified into different categories:

- **BASE**: Core functionality plugins (included in the base_plugins directory)
- **EXTRACTOR**: Plugins that extract information from resume text
- **PROCESSOR**: Plugins that process data after extraction
- **ANALYZER**: Plugins that analyze extracted data
- **CUSTOM**: User-created plugins for specific needs
- **UTILITY**: Helper plugins for various operations

## Creating Custom Plugins

### Plugin Structure

A basic plugin structure looks like this:

```python
from cvinsight.base_plugins import ExtractorPlugin, PluginMetadata, PluginCategory
from pydantic import BaseModel, Field
from typing import Dict, Any, Type, List

class CustomPlugin(ExtractorPlugin):
    """A custom plugin for specific extraction or analysis."""
    
    def __init__(self, llm_service=None):
        """Initialize the plugin with LLM service."""
        self.llm_service = llm_service
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="custom_extractor",
            version="1.0.0",
            description="Description of what this plugin does",
            category=PluginCategory.CUSTOM,
            author="Your Name"
        )
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass
    
    def get_model(self) -> Type[BaseModel]:
        """Define the Pydantic model for the output."""
        class CustomData(BaseModel):
            field1: str = Field(..., description="First field")
            field2: List[str] = Field(default_factory=list, description="Second field")
        
        return CustomData
    
    def get_prompt_template(self) -> str:
        """Define the prompt template for the LLM."""
        return """
        Extract specific information from the following text:
        
        {text}
        
        {format_instructions}
        """
    
    def get_input_variables(self) -> List[str]:
        """Define the input variables for the prompt template."""
        return ["text"]
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        """Prepare input data for the prompt template."""
        return {"text": extracted_text}
```

### Required Methods

Every plugin must implement these methods:

1. **metadata**
   - Returns a `PluginMetadata` object with plugin information
   - Includes name, version, description, category, and author

2. **initialize**
   - Called when the plugin is loaded
   - Used for any setup operations

3. **get_model**
   - Returns a Pydantic model class
   - Defines the structure of the output data

4. **get_prompt_template**
   - Returns a string template for the LLM prompt
   - Should include placeholders for input variables

5. **get_input_variables**
   - Returns a list of variable names used in the prompt template
   - Must include at least the text input variable

6. **prepare_input_data**
   - Prepares the input data for the prompt template
   - Takes extracted text and returns a dictionary of variables

### Plugin Metadata

The `PluginMetadata` class includes:

```python
class PluginMetadata:
    name: str           # Unique identifier for the plugin
    version: str        # Version number (semantic versioning recommended)
    description: str    # Brief description of what the plugin does
    category: str       # Plugin category (use PluginCategory enum)
    author: str         # Plugin author name
```

The `PluginCategory` enum includes these options:
```python
class PluginCategory:
    BASE = "BASE"           # Core functionality
    EXTRACTOR = "EXTRACTOR" # Data extraction
    PROCESSOR = "PROCESSOR" # Data processing
    ANALYZER = "ANALYZER"   # Data analysis
    CUSTOM = "CUSTOM"       # Custom functionality
    UTILITY = "UTILITY"     # Utility functions
```

### Using Pydantic Models

Pydantic models define the structure of your plugin's output:

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class CustomModel(BaseModel):
    """Model for custom extracted data."""
    name: str = Field(..., description="Name of the entity")
    categories: List[str] = Field(default_factory=list, description="Categories")
    description: Optional[str] = Field(None, description="Optional description")
```

### Practical Example: Job Match Analyzer

Here's a complete example of a job matcher plugin:

```python
from cvinsight.base_plugins import ExtractorPlugin, PluginMetadata, PluginCategory
from pydantic import BaseModel, Field
from typing import Dict, Any, Type, List

class JobMatch(BaseModel):
    """Model for job match analysis."""
    match_score: int = Field(..., description="Match score from 0-100")
    matching_skills: List[str] = Field(default_factory=list, description="Matching skills")
    missing_skills: List[str] = Field(default_factory=list, description="Missing required skills")
    recommendation: str = Field(..., description="Overall recommendation")

class JobMatchPlugin(ExtractorPlugin):
    """Plugin to match resumes against job descriptions."""
    
    def __init__(self, job_description: str, llm_service=None):
        """
        Initialize with a job description.
        
        Args:
            job_description: The job description to match against
            llm_service: LLM service for extraction
        """
        self.job_description = job_description
        self.llm_service = llm_service
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="job_match_analyzer",
            version="1.0.0",
            description="Analyzes how well a resume matches a job description",
            category=PluginCategory.ANALYZER,
            author="Your Name"
        )
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass
    
    def get_model(self) -> Type[BaseModel]:
        """Get the Pydantic model for job match analysis."""
        return JobMatch
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for job matching."""
        return """
        Analyze how well the candidate's resume matches the following job description.
        Provide a match score from 0-100, list matching skills, missing required skills,
        and give an overall recommendation.
        
        JOB DESCRIPTION:
        {job_description}
        
        RESUME:
        {text}
        
        {format_instructions}
        """
    
    def get_input_variables(self) -> List[str]:
        """Get the input variables for the prompt template."""
        return ["text", "job_description"]
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        """Prepare the input data for the LLM."""
        return {
            "text": extracted_text,
            "job_description": self.job_description
        }
```

## Using Custom Plugins

### With the Client Interface

```python
from cvinsight import CVInsightClient
from your_plugins import JobMatchPlugin

# Initialize the client
client = CVInsightClient()

# Create the custom plugin
job_description = "Looking for a Python developer with 3+ years of experience..."
job_match_plugin = JobMatchPlugin(job_description)

# Register your plugin with the client
client._plugin_manager.register_plugin(job_match_plugin)

# Process a resume with your custom plugin
result = client.extract_all("path/to/resume.pdf")

# Access the results from your custom plugin
match_data = result.get("job_match_analyzer", {})
print(f"Match score: {match_data.get('match_score')}/100")
```

### Registering Multiple Plugins

```python
from cvinsight import CVInsightClient
from your_plugins import JobMatchPlugin, SkillsCategorizer, KeywordAnalyzer

# Initialize the client
client = CVInsightClient()

# Create and register multiple plugins
plugins = [
    JobMatchPlugin("Software Developer job description..."),
    SkillsCategorizer(),
    KeywordAnalyzer(keywords=["python", "machine learning", "data science"])
]

# Register all plugins
for plugin in plugins:
    client._plugin_manager.register_plugin(plugin)

# Process a resume with all registered plugins
result = client.extract_all("path/to/resume.pdf")
```

## Plugin Best Practices

1. **Focus on Single Responsibility**
   - Each plugin should do one thing well
   - Split complex functionality into multiple plugins

2. **Optimize Prompts**
   - Keep prompts clear and concise
   - Only request necessary information
   - Use examples for complex formats

3. **Handle Errors Gracefully**
   - Include error handling in your plugins
   - Provide default values for missing data
   - Log meaningful error messages

4. **Token Usage**
   - Monitor and optimize token usage
   - Avoid unnecessarily large prompts
   - Consider batching related requests

5. **Testing**
   - Test plugins with various resume formats
   - Verify output structure matches your model
   - Check edge cases and error handling

## Advanced Plugin Topics

### Plugin Dependencies

If your plugin depends on other plugins:

```python
class DependentPlugin(ExtractorPlugin):
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        self.dependencies = ["skills_extractor"]  # Plugin names this plugin depends on
    
    def process_resume(self, resume, extracted_text=None):
        # Access data from dependencies
        skills = resume.get("skills", [])
        # Process with dependency data
        return {"processed_skills": self.process_skills(skills)}
```

### Plugin Configuration

For configurable plugins:

```python
class ConfigurablePlugin(ExtractorPlugin):
    def __init__(self, config=None, llm_service=None):
        self.llm_service = llm_service
        self.config = config or {}
        
    def initialize(self) -> None:
        # Set defaults for missing config
        self.threshold = self.config.get("threshold", 0.5)
        self.max_results = self.config.get("max_results", 10)
```

### Stateful Plugins

If your plugin needs to maintain state:

```python
class StatefulPlugin(ExtractorPlugin):
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
        self.processed_count = 0
        self.results_cache = {}
        
    def extract(self, text):
        result, token_usage = super().extract(text)
        self.processed_count += 1
        self.results_cache[hash(text)] = result
        return result, token_usage
```
