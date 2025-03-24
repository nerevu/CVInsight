# Resume Analysis: Plugin-Based Architecture

## Overview
This guide explains how to use the new plugin-based architecture for the Resume Analysis tool. The plugin architecture provides a more flexible, modular, and extensible way to process resumes.

## Getting Started

### Running with Plugins
To run the Resume Analysis tool with the plugin-based architecture:

```bash
python main.py --resume path/to/your/resume.pdf
```

Additional options:
- `--verbose`: Enable detailed logging
- `--report-only`: Only show token usage report for previously processed resume
- `--log-dir`: Specify a directory for token usage logs
- `--cleanup`: Clean up __pycache__ directories and compiled Python files

### Available Plugins
The following plugins are included by default:

1. **Profile Extractor Plugin**: Extracts basic profile information (name, email, phone, etc.)
2. **Skills Extractor Plugin**: Extracts technical and soft skills
3. **Education Extractor Plugin**: Extracts education history
4. **Experience Extractor Plugin**: Extracts work experience history
5. **YoE Extractor Plugin**: Extracts years of experience

## Developing Custom Plugins

### Plugin Types
The system supports two main types of plugins:
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

### Creating an Extractor Plugin

#### Step 1: Create the Plugin Directory Structure
1. Create a new directory in `custom_plugins/your_plugin_name/`
2. Create an `__init__.py` file in that directory

#### Step 2: Define Your Data Model
If your plugin extracts structured data, define a Pydantic model for it:

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class YourCustomDataModel(BaseModel):
    """Model for your custom data"""
    main_field: str = Field(..., description="Primary data extracted by the plugin")
    secondary_field: Optional[List[str]] = Field(default_factory=list, 
                                               description="Secondary data extracted")
```

#### Step 3: Implement the Plugin Class
Create your plugin class in the `__init__.py` file:

```python
from typing import Dict, Any, Type, List, Tuple
from pydantic import BaseModel
from plugins.base import ExtractorPlugin, PluginMetadata, PluginCategory
from datetime import date

class YourCustomExtractorPlugin(ExtractorPlugin):
    """Your custom extractor plugin."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="your_custom_extractor",  # This will be used to reference the plugin
            version="1.0.0",
            description="Description of your extractor",
            category=PluginCategory.CUSTOM,
            author="Your Name"
        )
    
    def initialize(self) -> None:
        """Initialize the plugin. Called once during startup."""
        # Add any setup code here, such as loading resources
        pass
    
    def get_model(self) -> Type[BaseModel]:
        """Get the Pydantic model for the extractor."""
        return YourCustomDataModel
    
    def get_prompt_template(self) -> str:
        """Get the prompt template for the extractor."""
        return """
        You are an expert resume parser. Your task is to extract [your specific information] 
        from the resume text provided below.
        
        For each item, extract the following details:
        - Field 1: [instructions for field 1]
        - Field 2: [instructions for field 2]
        
        {format_instructions}
        
        Text:
        {text}
        """
    
    def get_input_variables(self) -> List[str]:
        """Get the input variables for the prompt template."""
        return ["text"]  # Add any other variables used in your prompt template
    
    def prepare_input_data(self, extracted_text: str) -> Dict[str, Any]:
        """Prepare the input data for the LLM."""
        return {
            "text": extracted_text,
            # Add any other variables needed by your prompt template
            # Example: "today": date.today().strftime("%d/%m/%Y")
        }
    
    def extract(self, text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract custom information from the text."""
        from llm_service import extract_with_llm
        
        # Prepare prompt from template
        prompt_template = self.get_prompt_template()
        input_data = self.prepare_input_data(text)
        input_variables = self.get_input_variables()
        model = self.get_model()
        
        # Call LLM service
        result, token_usage = extract_with_llm(
            model,
            prompt_template,
            input_variables,
            input_data
        )
        
        # Add extractor name to token usage
        token_usage["extractor"] = self.metadata.name
        
        # Process the result to ensure it has the expected structure
        processed_result = {}
        if isinstance(result, dict):
            processed_result = result
        elif hasattr(result, "model_dump"):
            # If result is a Pydantic model, convert to dict
            processed_result = result.model_dump()
        
        return processed_result, token_usage
```

#### Step 4: Creating a Processor Plugin
If your plugin processes data rather than extracting it:

```python
from plugins.base import BasePlugin, PluginMetadata, PluginCategory
from models.resume_models import Resume

class YourCustomProcessorPlugin(BasePlugin):
    """Your custom processor plugin."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="your_custom_processor",
            version="1.0.0",
            description="Description of your processor plugin",
            category=PluginCategory.PROCESSOR,
            author="Your Name"
        )
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        pass
    
    def process_resume(self, resume: Resume, extracted_text: str = None) -> Dict[str, Any]:
        """
        Process the resume after extraction has been done.
        
        Args:
            resume: The Resume object with extracted information
            extracted_text: Original text extracted from the resume (optional)
            
        Returns:
            Dictionary with processed data to add to resume.plugin_data
        """
        # Example: analyze and summarize skills
        all_skills = resume.skills
        
        # Your custom processing logic here
        result = {
            "summary": "Custom analysis of the resume",
            "recommendation": "Based on skills and experience..."
        }
        
        return result
```

### Registering Your Custom Plugin

#### Step 1: Add Your Plugin to the __all__ List
Edit the `custom_plugins/__init__.py` file and add your plugin class to the `__all__` list:

```python
"""Custom plugins for Resume Analysis."""

from typing import List

# Define the list of all custom plugins
__all__: List[str] = [
    "YourCustomExtractorPlugin"
]
```

#### Step 2: Import Your Plugin in custom_plugins/__init__.py (Optional)
For cleaner imports, you can also import your plugin in the custom_plugins/__init__.py file:

```python
"""Custom plugins for Resume Analysis."""

from typing import List
from custom_plugins.your_plugin_name import YourCustomExtractorPlugin

# Define the list of all custom plugins
__all__: List[str] = [
    "YourCustomExtractorPlugin"
]
```

### Enabling and Disabling Plugins

#### Disabling Specific Custom Plugins
To disable a specific custom plugin, comment it out or remove it from the `__all__` list in custom_plugins/__init__.py:

```python
# Define the list of all custom plugins
__all__: List[str] = [
    # "YourCustomExtractorPlugin"  # Commented out to disable this plugin
]
```

#### Disabling All Custom Plugins
To disable all custom plugins, set `ENABLE_CUSTOM_PLUGINS = False` in config.py:

```python
# Plugin system configuration
PLUGINS_DIR = os.environ.get("PLUGINS_DIR", "./plugins")
CUSTOM_PLUGINS_DIR = os.environ.get("CUSTOM_PLUGINS_DIR", "./custom_plugins")
ENABLE_CUSTOM_PLUGINS = False  # Set to False to disable all custom plugins
```

### Accessing Plugin Results

Custom plugin results are stored in the `plugin_data` dictionary of the Resume object. You can access them using the plugin's name:

```python
# Example code to access plugin data
resume_json = json.load(open("Results/example_resume.json"))
custom_plugin_results = resume_json.get("plugin_data", {}).get("your_custom_extractor", {})
```

### Using Results from Other Plugins

Your custom plugin can use data already extracted by other plugins. For processor plugins, this is provided via the Resume object:

```python
def process_resume(self, resume: Resume, extracted_text: str = None) -> Dict[str, Any]:
    # Access data from another plugin
    skills = resume.skills
    work_experience = resume.work_experiences
    
    # Use this data in your custom processing
    # ...
```

For more complex dependencies, you can request the plugin manager in your initialize method:

```python
def initialize(self, plugin_manager=None) -> None:
    self.plugin_manager = plugin_manager
    
def process_resume(self, resume: Resume, extracted_text: str = None) -> Dict[str, Any]:
    # Get results from another plugin if needed
    if self.plugin_manager:
        other_plugin = self.plugin_manager.get_plugin("other_plugin_name")
        if other_plugin:
            # Use the other plugin directly
            pass
```

## Advanced Plugin Development

### LLM Interaction Options

Plugins can interact with the LLM in various ways:

1. **Direct Extraction**: Using a prompt template and the extract_with_llm function (as shown above)
2. **Chained Extraction**: Making multiple LLM calls in sequence to refine results
3. **Batched Processing**: Processing data in batches to handle larger resumes
4. **Custom LLM Call**: Making custom calls to the LLM service for specialized needs

Example of a chained extraction:

```python
def extract(self, text: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    # First extraction for basic data
    first_result, token_usage = self.extract_basic_info(text)
    
    # Second extraction with more context
    enhanced_prompt = f"""
    Based on the following information extracted from a resume:
    {first_result}
    
    Please provide a detailed analysis of...
    """
    enhanced_result, enhanced_token_usage = self.extract_detailed_info(enhanced_prompt)
    
    # Combine token usage
    combined_token_usage = {
        "total_tokens": token_usage.get("total_tokens", 0) + enhanced_token_usage.get("total_tokens", 0),
        "prompt_tokens": token_usage.get("prompt_tokens", 0) + enhanced_token_usage.get("prompt_tokens", 0),
        "completion_tokens": token_usage.get("completion_tokens", 0) + enhanced_token_usage.get("completion_tokens", 0),
        "extractor": self.metadata.name
    }
    
    # Combine results
    combined_result = {**first_result, "detailed_analysis": enhanced_result}
    
    return combined_result, combined_token_usage
```

### Testing Your Plugin

To test your plugin during development:

1. Create a test script in your plugin directory:

```python
# custom_plugins/your_plugin_name/test_plugin.py
import os
import sys
import json
from custom_plugins.your_plugin_name import YourCustomExtractorPlugin
from utils.file_utils import read_file

def test_plugin():
    # Create plugin instance
    plugin = YourCustomExtractorPlugin()
    plugin.initialize()
    
    # Load a test resume
    test_resume_path = "path/to/test/resume.pdf"
    resume_text = read_file(test_resume_path)
    
    # Run extraction
    result, token_usage = plugin.extract(resume_text)
    
    # Print results
    print(f"Extraction result: {json.dumps(result, indent=2)}")
    print(f"Token usage: {token_usage}")

if __name__ == "__main__":
    test_plugin()
```

2. Run the test script:
```bash
python -m custom_plugins.your_plugin_name.test_plugin
```

### Configuration and Environment Variables

Your plugin can use configuration settings from the config.py file and environment variables:

```python
import config
import os

def initialize(self) -> None:
    # Access configuration
    self.model_name = config.LLM_MODEL
    self.temperature = config.LLM_TEMPERATURE
    
    # Custom plugin config (add to config.py for your plugin)
    self.custom_setting = os.environ.get("YOUR_PLUGIN_SETTING", "default_value")
```

## Plugin Lifecycle

1. **Discovery**: The Plugin Manager scans both base_plugins and custom_plugins directories
2. **Filtering**: Only plugins listed in the `__all__` list in each directory's __init__.py are considered
3. **Instantiation**: Each plugin class is instantiated
4. **Initialization**: The `initialize()` method is called on each plugin
5. **Registration**: Plugins are registered with the Plugin Manager by name
6. **Extraction**: For resume processing, extractor plugins are called to extract data
7. **Processing**: After extraction, processor plugins are called to process the extracted data
8. **Integration**: Results are combined into a unified Resume object
9. **Storage**: The processed resume is saved to JSON

## Architecture Design

### Key Components

1. **Plugin Manager**: Handles plugin discovery, loading, and management
2. **Plugin Resume Processor**: Uses plugins to process resumes
3. **Base Plugin Interface**: Defines the interface for all plugins
4. **Extractor Plugin Interface**: Specializes the base interface for data extraction
5. **Resume Models**: Defines the data structures for storing extracted information
6. **LLM Service**: Provides access to the language model for extractors

### Data Flow in the Plugin System

1. **Text Extraction**: Resume text is extracted from PDF/DOCX files
2. **Parallel Processing**: Multiple extractor plugins process the text concurrently 
3. **Synchronization**: Results from all extractors are collected
4. **Post-Processing**: Results are processed by processor plugins
5. **Aggregation**: All results are combined into a single Resume object
6. **Serialization**: The Resume object is saved as JSON

## Common Pitfalls and Troubleshooting

### Plugin Not Loading
- Ensure your plugin class is listed in the `__all__` list in custom_plugins/__init__.py
- Check that ENABLE_CUSTOM_PLUGINS is True in config.py
- Verify that your plugin class inherits from BasePlugin or ExtractorPlugin
- Check the logs for any error messages during plugin discovery and loading

### LLM API Errors
- Verify your API key is correctly set in the .env file
- Check if you've reached API rate limits
- Ensure your prompt template is properly formatted

### Result Formatting Issues
- Validate that your Pydantic model matches the expected output format
- Ensure the format_instructions in your prompt template is included
- Check that the LLM understands how to format the output correctly

### Performance Issues
- Consider batching or chunking large resumes
- Implement caching for expensive operations
- Use concurrent processing where appropriate

## Examples of Custom Plugins

### Keyword Matcher Plugin
```python
# custom_plugins/keyword_matcher/__init__.py
from typing import Dict, Any, List, Tuple
from plugins.base import BasePlugin, PluginMetadata, PluginCategory
from models.resume_models import Resume

class KeywordMatcherPlugin(BasePlugin):
    """Plugin to match keywords in a resume against a job description."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="keyword_matcher",
            version="1.0.0",
            description="Matches resume keywords against job requirements",
            category=PluginCategory.ANALYZER,
            author="Resume Analysis Team"
        )
    
    def initialize(self) -> None:
        # Initialize any resources needed
        self.job_keywords = {
            "technical": ["python", "javascript", "sql", "aws", "machine learning"],
            "soft": ["communication", "leadership", "teamwork", "problem solving"]
        }
    
    def process_resume(self, resume: Resume, extracted_text: str = None) -> Dict[str, Any]:
        """Match resume skills against keyword lists."""
        matches = {
            "technical": [],
            "soft": []
        }
        
        # Get skills from the resume
        skills = [s.lower() for s in resume.skills]
        
        # Match against technical keywords
        for keyword in self.job_keywords["technical"]:
            if any(keyword in skill.lower() for skill in skills):
                matches["technical"].append(keyword)
        
        # Match against soft skills
        for keyword in self.job_keywords["soft"]:
            if any(keyword in skill.lower() for skill in skills):
                matches["soft"].append(keyword)
        
        # Calculate match percentage
        total_keywords = len(self.job_keywords["technical"]) + len(self.job_keywords["soft"])
        total_matches = len(matches["technical"]) + len(matches["soft"])
        match_percentage = (total_matches / total_keywords) * 100 if total_keywords > 0 else 0
        
        return {
            "matched_keywords": matches,
            "match_percentage": round(match_percentage, 2)
        }
```

## Benefits of the Plugin Architecture

1. **Modularity**: Each extraction functionality is encapsulated
2. **Extensibility**: New extractors can be added without modifying core code
3. **Maintainability**: Easier to update individual components
4. **Customization**: Users can develop specialized extractors
5. **Reusability**: Plugins can be shared and reused across projects
6. **Isolation**: Errors in one plugin don't affect others
7. **Scalability**: New capabilities can be added incrementally

## Advanced Troubleshooting

If you encounter issues with the plugin system:

1. Enable verbose logging with `--verbose`
2. Check the log file (resume_analysis.log) for detailed error messages
3. Verify that all required Python packages are installed
4. Check for circular imports in your plugin code
5. Ensure your plugin follows the correct interface
6. Verify the file doesn't contain null bytes (clean with `python -m utils.cleanup`)
7. Check Python version compatibility (recommended: Python 3.8+)

For more help, consult the plugin system documentation or open an issue in the repository. 