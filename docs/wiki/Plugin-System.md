# Plugin System

The Resume Analysis tool uses a flexible plugin-based architecture that allows you to extend its functionality by creating custom plugins. This guide explains the plugin system and how to create your own plugins.

## Plugin Architecture Overview

### Core Components

1. **Plugin Manager**
   - Discovers and loads plugins
   - Manages plugin lifecycle
   - Handles plugin dependencies

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

1. **ProfileExtractorPlugin**
   - Extracts basic information
   - Name, contact details, email

2. **SkillsExtractorPlugin**
   - Identifies skills from resume
   - Technical and soft skills

3. **EducationExtractorPlugin**
   - Extracts educational history
   - Institutions, degrees, dates

4. **ExperienceExtractorPlugin**
   - Analyzes work experience
   - Companies, roles, dates

5. **YoeExtractorPlugin**
   - Calculates years of experience
   - Total professional experience

## Creating Custom Plugins

### Plugin Structure

A basic plugin structure looks like this:

```python
from base_plugins.base import BasePlugin

class CustomPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        
    @property
    def name(self) -> str:
        return "CustomPlugin"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Description of what this plugin does"
        
    @property
    def category(self) -> str:
        return "custom"
        
    def get_model(self) -> str:
        return "gemini-2.0-flash"
        
    def get_prompt_template(self) -> str:
        return """
        Extract {category} information from the following resume text:
        
        {resume_text}
        
        Return the information in the following JSON format:
        {
            "key1": "value1",
            "key2": ["value2", "value3"]
        }
        """
        
    def process_output(self, output: str) -> dict:
        # Process the LLM output and return structured data
        return self.parse_json(output)
```

### Required Methods

Every plugin must implement these methods:

1. **name**
   - Returns unique plugin name
   - Used for identification and logging

2. **version**
   - Returns plugin version
   - Helps with compatibility tracking

3. **description**
   - Returns plugin description
   - Used in documentation and UI

4. **category**
   - Returns plugin category
   - Groups related plugins

5. **get_model**
   - Returns LLM model name
   - Specifies which model to use

6. **get_prompt_template**
   - Returns prompt template
   - Defines how to query the LLM

7. **process_output**
   - Processes LLM output
   - Returns structured data

### Best Practices

1. **Plugin Design**
   - Keep plugins focused and single-purpose
   - Use clear, descriptive names
   - Document all methods and parameters

2. **Error Handling**
   - Implement robust error handling
   - Validate LLM outputs
   - Provide meaningful error messages

3. **Performance**
   - Optimize prompt templates
   - Minimize token usage
   - Handle large inputs efficiently

4. **Testing**
   - Write unit tests
   - Test with various inputs
   - Verify output formats

## Plugin Development Guide

### 1. Create Plugin File

Create a new Python file in the `custom_plugins` directory:

```python
# custom_plugins/custom_extractor.py
from base_plugins.base import BasePlugin

class CustomExtractorPlugin(BasePlugin):
    # Implement required methods
    pass
```

### 2. Register Plugin

Add your plugin to `custom_plugins/__init__.py`:

```python
from .custom_extractor import CustomExtractorPlugin

__all__ = ['CustomExtractorPlugin']
```

### 3. Test Plugin

Create tests in `tests/test_custom_extractor.py`:

```python
import unittest
from custom_plugins.custom_extractor import CustomExtractorPlugin

class TestCustomExtractor(unittest.TestCase):
    def setUp(self):
        self.plugin = CustomExtractorPlugin()
        
    def test_plugin_initialization(self):
        self.assertEqual(self.plugin.name, "CustomExtractorPlugin")
        self.assertEqual(self.plugin.version, "1.0.0")
        
    def test_plugin_processing(self):
        # Test plugin processing
        pass

if __name__ == '__main__':
    unittest.main()
```

## Plugin Examples

### 1. Skills Extractor Plugin

```python
from base_plugins.base import BasePlugin

class SkillsExtractorPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        
    @property
    def name(self) -> str:
        return "SkillsExtractorPlugin"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Extracts skills from resume text"
        
    @property
    def category(self) -> str:
        return "skills"
        
    def get_model(self) -> str:
        return "gemini-2.0-flash"
        
    def get_prompt_template(self) -> str:
        return """
        Extract skills from the following resume text.
        Include both technical and soft skills.
        
        Resume text:
        {resume_text}
        
        Return a JSON array of skills:
        ["skill1", "skill2", ...]
        """
        
    def process_output(self, output: str) -> dict:
        skills = self.parse_json(output)
        return {"skills": skills}
```

### 2. Experience Extractor Plugin

```python
from base_plugins.base import BasePlugin

class ExperienceExtractorPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        
    @property
    def name(self) -> str:
        return "ExperienceExtractorPlugin"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Extracts work experience from resume"
        
    @property
    def category(self) -> str:
        return "experience"
        
    def get_model(self) -> str:
        return "gemini-2.0-flash"
        
    def get_prompt_template(self) -> str:
        return """
        Extract work experience from the resume text.
        For each position, include:
        - Company name
        - Role/title
        - Start date
        - End date
        - Location
        
        Resume text:
        {resume_text}
        
        Return a JSON array of experiences:
        [
            {
                "company": "Company Name",
                "role": "Job Title",
                "start_date": "YYYY-MM",
                "end_date": "YYYY-MM",
                "location": "City, Country"
            },
            ...
        ]
        """
        
    def process_output(self, output: str) -> dict:
        experiences = self.parse_json(output)
        return {"work_experiences": experiences}
```

## Plugin Management

### Loading Plugins

The system automatically loads plugins from:
1. `base_plugins/` directory
2. `custom_plugins/` directory

### Plugin Configuration

Plugins can be configured through:
1. Environment variables
2. Configuration files
3. Command-line arguments

### Plugin Dependencies

Handle plugin dependencies by:
1. Declaring dependencies in plugin metadata
2. Checking dependencies during initialization
3. Loading dependencies in correct order

## Next Steps

- Review the [Technical Documentation](Technical-Documentation) for detailed technical documentation
- Check out the [Examples & Tutorials](Examples-and-Tutorials) for more plugin examples
- Join the community to share and learn about plugins 