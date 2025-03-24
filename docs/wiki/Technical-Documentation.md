# Technical Documentation

This page provides detailed technical documentation about the internal implementation of the Resume Analysis tool.

## Core Classes

### BasePlugin

The abstract base class for all plugins.

```python
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the unique name of the plugin."""
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """Returns the version of the plugin."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Returns a description of what the plugin does."""
        pass
        
    @property
    @abstractmethod
    def category(self) -> str:
        """Returns the category of the plugin."""
        pass
        
    @abstractmethod
    def get_model(self) -> str:
        """Returns the LLM model to use."""
        pass
        
    @abstractmethod
    def get_prompt_template(self) -> str:
        """Returns the prompt template for the LLM."""
        pass
        
    @abstractmethod
    def process_output(self, output: str) -> dict:
        """Processes the LLM output and returns structured data."""
        pass
        
    def parse_json(self, text: str) -> dict:
        """Utility method to parse JSON from text."""
        pass
```

### PluginManager

Manages plugin discovery and loading.

```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
        
    def load_plugins(self):
        """Loads all available plugins."""
        pass
        
    def get_plugin(self, name: str) -> BasePlugin:
        """Returns a plugin by name."""
        pass
        
    def get_plugins_by_category(self, category: str) -> list:
        """Returns all plugins in a category."""
        pass
```

### ResumeProcessor

Processes resumes using plugins.

```python
class ResumeProcessor:
    def __init__(self, plugins: list[BasePlugin]):
        self.plugins = plugins
        
    async def process_resume(self, resume_text: str) -> dict:
        """Processes a resume using all plugins concurrently."""
        pass
        
    def process_resume_sync(self, resume_text: str) -> dict:
        """Processes a resume synchronously."""
        pass
```

### LLMService

Handles interactions with the LLM API.

```python
class LLMService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    async def generate(self, prompt: str, model: str) -> str:
        """Generates text using the LLM."""
        pass
        
    def get_token_count(self, text: str) -> int:
        """Returns the token count for text."""
        pass
```

## Data Models

### ResumeData

```python
@dataclass
class ResumeData:
    name: str
    contact_number: str
    email: str
    skills: list[str]
    educations: list[Education]
    work_experiences: list[Experience]
    YoE: str
```

### Education

```python
@dataclass
class Education:
    institution: str
    start_date: str
    end_date: str
    location: str
    degree: str
```

### Experience

```python
@dataclass
class Experience:
    company: str
    start_date: str
    end_date: str
    location: str
    role: str
```

## Configuration

### Environment Variables

```python
class Config:
    GOOGLE_API_KEY: str
    DEFAULT_LLM_MODEL: str
    RESUME_DIR: str
    OUTPUT_DIR: str
    LOG_LEVEL: str
    LOG_FILE: str
    TOKEN_LOG_RETENTION_DAYS: int
    LOG_MAX_SIZE_MB: int
    LOG_BACKUP_COUNT: int
    DEBUG: bool
```

## Utility Functions

### File Handling

```python
def read_resume_file(file_path: str) -> str:
    """Reads and extracts text from a resume file."""
    pass
    
def save_results(results: dict, output_path: str):
    """Saves processing results to a file."""
    pass
```

### Logging

```python
def setup_logging(log_level: str, log_file: str):
    """Sets up logging configuration."""
    pass
    
def log_token_usage(resume_file: str, usage: dict):
    """Logs token usage information."""
    pass
```

### JSON Processing

```python
def parse_json(text: str) -> dict:
    """Parses JSON from text."""
    pass
    
def format_json(data: dict) -> str:
    """Formats data as JSON string."""
    pass
```

## Error Handling

### Custom Exceptions

```python
class PluginError(Exception):
    """Base exception for plugin-related errors."""
    pass
    
class LLMError(Exception):
    """Exception for LLM-related errors."""
    pass
    
class FileError(Exception):
    """Exception for file-related errors."""
    pass
```

## Async Support

The implementation provides both synchronous and asynchronous interfaces:

```python
# Synchronous
processor = ResumeProcessor(plugins)
results = processor.process_resume_sync(resume_text)

# Asynchronous
async def process_resume():
    processor = ResumeProcessor(plugins)
    results = await processor.process_resume(resume_text)
```

## Type Hints

All functions and methods include type hints for better IDE support:

```python
from typing import List, Dict, Optional

def process_resume(
    text: str,
    plugins: List[BasePlugin]
) -> Dict[str, Any]:
    pass
```

## Constants

```python
# File extensions
PDF_EXTENSION = ".pdf"
DOCX_EXTENSION = ".docx"

# Log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Default values
DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = "resume_analysis.log"
```

## Best Practices

1. **Error Handling**
   - Use custom exceptions for specific error cases
   - Provide meaningful error messages
   - Log errors appropriately

2. **Type Safety**
   - Use type hints consistently
   - Validate input data
   - Handle edge cases

3. **Performance**
   - Use async/await for I/O operations
   - Implement caching where appropriate
   - Optimize resource usage

4. **Testing**
   - Write unit tests for all components
   - Test edge cases and error conditions
   - Mock external dependencies

## Next Steps

- Review the [Plugin System](Plugin-System) documentation
- Check out the [Examples & Tutorials](Examples-and-Tutorials)
- Join the community for support and discussions 