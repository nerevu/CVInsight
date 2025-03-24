# Examples & Tutorials

This page provides practical examples and tutorials for using the Resume Analysis tool.

## Basic Usage Examples

### 1. Process a Single Resume

```python
from resume_processor import ResumeProcessor
from plugin_manager import PluginManager

# Initialize plugin manager and load plugins
plugin_manager = PluginManager()
plugin_manager.load_plugins()

# Create resume processor with all plugins
processor = ResumeProcessor(plugin_manager.get_all_plugins())

# Process a single resume
results = processor.process_resume_sync("path/to/resume.pdf")
print(results)
```

### 2. Process Multiple Resumes

```python
import asyncio
from pathlib import Path

async def process_multiple_resumes():
    # Initialize components
    plugin_manager = PluginManager()
    plugin_manager.load_plugins()
    processor = ResumeProcessor(plugin_manager.get_all_plugins())
    
    # Get all resume files
    resume_dir = Path("Resumes")
    resume_files = list(resume_dir.glob("*.pdf")) + list(resume_dir.glob("*.docx"))
    
    # Process all resumes concurrently
    tasks = [processor.process_resume(str(file)) for file in resume_files]
    results = await asyncio.gather(*tasks)
    
    return results

# Run the async function
results = asyncio.run(process_multiple_resumes())
```

### 3. Custom Plugin Example

```python
from base_plugins.base import BasePlugin

class CertificationExtractorPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        
    @property
    def name(self) -> str:
        return "CertificationExtractorPlugin"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Extracts certifications from resume"
        
    @property
    def category(self) -> str:
        return "certifications"
        
    def get_model(self) -> str:
        return "gemini-2.0-flash"
        
    def get_prompt_template(self) -> str:
        return """
        Extract certifications from the resume text.
        For each certification, include:
        - Name of certification
        - Issuing organization
        - Date obtained
        - Expiration date (if applicable)
        
        Resume text:
        {resume_text}
        
        Return a JSON array of certifications:
        [
            {
                "name": "Certification Name",
                "organization": "Issuing Organization",
                "date_obtained": "YYYY-MM",
                "expiration_date": "YYYY-MM"
            },
            ...
        ]
        """
        
    def process_output(self, output: str) -> dict:
        certifications = self.parse_json(output)
        return {"certifications": certifications}
```

## Advanced Tutorials

### 1. Custom Plugin Development

This tutorial shows how to create a custom plugin for extracting project experience.

```python
from base_plugins.base import BasePlugin
from typing import List, Dict, Any

class ProjectExperiencePlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        
    @property
    def name(self) -> str:
        return "ProjectExperiencePlugin"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Extracts project experience from resume"
        
    @property
    def category(self) -> str:
        return "projects"
        
    def get_model(self) -> str:
        return "gemini-2.0-flash"
        
    def get_prompt_template(self) -> str:
        return """
        Extract project experience from the resume text.
        For each project, include:
        - Project name
        - Description
        - Technologies used
        - Duration
        - Role in project
        
        Resume text:
        {resume_text}
        
        Return a JSON array of projects:
        [
            {
                "name": "Project Name",
                "description": "Project description",
                "technologies": ["tech1", "tech2"],
                "duration": "X months",
                "role": "Role in project"
            },
            ...
        ]
        """
        
    def process_output(self, output: str) -> Dict[str, Any]:
        projects = self.parse_json(output)
        return {"projects": projects}
        
    def validate_output(self, data: Dict[str, Any]) -> bool:
        """Validate the processed output."""
        if not isinstance(data.get("projects"), list):
            return False
            
        for project in data["projects"]:
            required_fields = ["name", "description", "technologies", "duration", "role"]
            if not all(field in project for field in required_fields):
                return False
                
        return True
```

### 2. Token Usage Optimization

This tutorial demonstrates how to optimize token usage in plugins.

```python
from base_plugins.base import BasePlugin
from llm_service import LLMService

class OptimizedPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.llm_service = LLMService()
        
    def get_prompt_template(self) -> str:
        return """
        Extract {category} from resume.
        Format: JSON array of items.
        
        Text: {resume_text}
        """
        
    async def process_with_retry(self, text: str, max_retries: int = 3) -> dict:
        """Process with retry logic and token optimization."""
        for attempt in range(max_retries):
            try:
                # Get token count
                token_count = self.llm_service.get_token_count(text)
                
                # If text is too long, truncate it
                if token_count > 4000:  # Example limit
                    text = self.truncate_text(text)
                
                # Process with optimized prompt
                output = await self.llm_service.generate(
                    self.get_prompt_template().format(
                        category=self.category,
                        resume_text=text
                    ),
                    self.get_model()
                )
                
                return self.process_output(output)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)  # Wait before retry
                
    def truncate_text(self, text: str, max_tokens: int = 4000) -> str:
        """Truncate text to fit within token limit."""
        # Implementation of text truncation
        pass
```

### 3. Concurrent Processing

This tutorial shows how to implement efficient concurrent processing of resumes.

```python
import asyncio
from typing import List, Dict
from pathlib import Path
from resume_processor import ResumeProcessor
from plugin_manager import PluginManager

class ConcurrentResumeProcessor:
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins()
        self.processor = ResumeProcessor(self.plugin_manager.get_all_plugins())
        
    async def process_batch(self, resume_files: List[Path]) -> List[Dict]:
        """Process a batch of resumes with controlled concurrency."""
        results = []
        
        # Process files in chunks to control concurrency
        for i in range(0, len(resume_files), self.max_concurrent):
            chunk = resume_files[i:i + self.max_concurrent]
            tasks = [self.processor.process_resume(str(file)) for file in chunk]
            chunk_results = await asyncio.gather(*tasks)
            results.extend(chunk_results)
            
            # Optional: Add delay between chunks
            if i + self.max_concurrent < len(resume_files):
                await asyncio.sleep(1)
                
        return results
        
    async def process_directory(self, directory: str) -> List[Dict]:
        """Process all resumes in a directory."""
        resume_dir = Path(directory)
        resume_files = list(resume_dir.glob("*.pdf")) + list(resume_dir.glob("*.docx"))
        return await self.process_batch(resume_files)

# Usage example
async def main():
    processor = ConcurrentResumeProcessor(max_concurrent=5)
    results = await processor.process_directory("Resumes")
    print(f"Processed {len(results)} resumes")

if __name__ == "__main__":
    asyncio.run(main())
```

## Best Practices

### 1. Plugin Development

- Keep plugins focused and single-purpose
- Implement proper error handling
- Validate LLM outputs
- Optimize prompt templates
- Write comprehensive tests

### 2. Performance Optimization

- Use async/await for I/O operations
- Implement caching where appropriate
- Monitor token usage
- Handle large inputs efficiently
- Use concurrent processing for multiple resumes

### 3. Error Handling

- Implement retry logic for API calls
- Validate input data
- Handle edge cases
- Provide meaningful error messages
- Log errors appropriately

## Next Steps

- Review the [Technical Documentation](Technical-Documentation) for detailed technical documentation
- Check out the [Plugin System](Plugin-System) guide for more plugin examples
- Join the community to share and learn from others 