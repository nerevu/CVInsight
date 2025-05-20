# FAQ & Troubleshooting

This page provides answers to frequently asked questions and solutions to common issues with the CVInsight package.

## General Questions

### What is CVInsight?

CVInsight is a Python package that uses Large Language Models (LLMs) to automatically extract and analyze information from resumes. It supports both PDF and DOCX formats and uses a plugin-based architecture for extensibility.

### What are the system requirements?

- Python 3.9 or higher
- Google API key for Gemini LLM
- Sufficient disk space for processing resumes
- Internet connection for API access

### What resume formats are supported?

Currently supported formats:
- PDF (.pdf)
- DOCX (.docx)

## Installation Issues

### Q: How do I install the package?

A: Use pip:
```bash
pip install cvinsight
```

To install from source:
```bash
git clone https://github.com/Gaurav-Kumar98/CVInsight.git
cd CVInsight
pip install -e .
```

### Q: I'm getting dependency installation errors. What should I do?

A: Try these solutions:
1. Update pip: `python -m pip install --upgrade pip`
2. Install Visual C++ build tools (Windows)
3. Check Python version compatibility (Python 3.9+ required)
4. Install dependencies manually: `pip install -r requirements.txt`

### Q: How do I set up my Google API key?

A:
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Create a new API key
3. Use it in your code:
   ```python
   client = CVInsightClient(api_key="your_google_api_key")
   ```
4. Or set as environment variable:
   ```bash
   # Linux/Mac
   export GOOGLE_API_KEY=your_google_api_key
   # Windows PowerShell
   $env:GOOGLE_API_KEY="your_google_api_key"
   ```

## Usage Questions

### Q: How do I process a resume programmatically?

A: Use the client interface:
```python
from cvinsight import CVInsightClient

client = CVInsightClient()
results = client.extract_all("path/to/resume.pdf")
```

### Q: How do I use the command-line interface?

A: After installing the package:
```bash
# Process a resume
cvinsight --resume path/to/resume.pdf

# List available plugins
cvinsight --list-plugins

# Process with specific plugins
cvinsight --resume path/to/resume.pdf --plugins profile_extractor,skills_extractor
```

### Q: Where are the results saved?

A: When using the CLI with `--output` flag:
```bash
cvinsight --resume path/to/resume.pdf --output ./results
```

Otherwise, results are returned as a Python dictionary or JSON (with `--json` flag).

### Q: How do I view token usage?

A: Token usage is tracked automatically and saved to log files in the `logs` directory. You can also access token usage programmatically:

```python
results = client.extract_all("path/to/resume.pdf", log_token_usage=True)
# Check the logs directory for detailed token usage
```

## Plugin Questions

### Q: How do I create a custom plugin?

A: See the [Plugin System](Plugin-System) guide for detailed instructions. Here's a basic example:

```python
from cvinsight.base_plugins import ExtractorPlugin, PluginMetadata, PluginCategory
from pydantic import BaseModel, Field
from typing import Dict, Any, Type, List

class CustomPlugin(ExtractorPlugin):
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="custom_plugin",
            version="1.0.0",
            description="Custom plugin description",
            category=PluginCategory.CUSTOM,
            author="Your Name"
        )
    
    # Implement other required methods...
```

### Q: How do I use my custom plugin?

A: Register it with the client:

```python
from cvinsight import CVInsightClient
from your_module import CustomPlugin

client = CVInsightClient()
custom_plugin = CustomPlugin()
client._plugin_manager.register_plugin(custom_plugin)
results = client.extract_all("path/to/resume.pdf")
```

### Q: How do I see what plugins are available?

A: Use the client or CLI:

```python
# Using the client
plugins = client.list_all_plugins()
for plugin in plugins:
    print(f"{plugin['name']}: {plugin['description']}")
```

```bash
# Using the CLI
cvinsight --list-plugins
```

## Common Issues

### API Errors

#### Q: I'm getting "API key invalid" errors. What should I do?

A:
1. Verify your API key is correct
2. Check if the key has access to Gemini models
3. Ensure no extra spaces in the key
4. Try regenerating the key

#### Q: I'm getting rate limit errors. How can I fix this?

A:
1. Implement rate limiting in your code
2. Reduce concurrent requests
3. Monitor token usage and requests
4. Check Google's rate limits and quotas

### Processing Errors

#### Q: The package isn't extracting information correctly. What's wrong?

A:
1. Check resume format and readability
2. Use the right file type (PDF or DOCX)
3. Try extracting specific information (profile, skills, etc.)
4. Check for OCR issues in scanned documents

#### Q: I get import errors when using the package. How do I fix them?

A:
1. Verify the package is installed: `pip list | grep cvinsight`
2. Check your Python version (3.9+ required)
3. Make sure all dependencies are installed
4. Use the correct import paths: `from cvinsight import CVInsightClient`

### File Issues

#### Q: The package can't read my PDF file. What should I do?

A:
1. Check if the PDF is corrupted
2. Verify file permissions
3. Try converting to DOCX
4. Ensure the file is text-based (not scanned images without OCR)

#### Q: I'm getting "file not found" errors. How to fix?

A:
1. Verify file paths (use absolute paths if necessary)
2. Check directory permissions
3. Ensure files exist
4. Try different slashes for paths on Windows

## Package-Specific Issues

### Q: How do I handle package version conflicts?

A:
1. Create a virtual environment: `python -m venv venv`
2. Install in the virtual environment
3. Use `pip install -e .` for development
4. Specify exact versions in requirements

### Q: The CLI tool isn't available after installation. What's wrong?

A:
1. Make sure the package was installed correctly
2. Check if the scripts directory is in your PATH
3. Try reinstalling: `pip install --force-reinstall cvinsight`
4. On Windows, check for `.exe` extension

### Q: Is CVInsight compatible with my ATS system?

A:
1. The package returns structured data that can be integrated
2. Use the API to programmatically process resumes
3. Build a custom integration using the plugin system
4. Contact us for enterprise integration support

### Q: How can I optimize token usage to reduce costs?

A:
1. Use specific extractors instead of extract_all when possible
2. Create optimized prompt templates in custom plugins
3. Implement caching for repeat processing
4. Monitor token usage logs regularly

## Free Tier Limitations

### Q: What are the limits of Google's free tier for Gemini API?

A:
- Input and output tokens are free
- Rate limits:
  - 15 requests per minute (RPM)
  - 1,000,000 tokens per minute (TPM)
  - 1,500 requests per day (RPD)

### Q: How many resumes can I process with the free tier?

A:
- About 130 resumes per minute (token limit)
- Up to 1,500 resumes per day (request limit)
- Adequate for personal, small business, or medium-sized recruiting operations 