# FAQ & Troubleshooting

This page provides answers to frequently asked questions and solutions to common issues.

## General Questions

### What is Resume Analysis?

Resume Analysis is a Python-based tool that uses Large Language Models (LLMs) to automatically extract and analyze information from resumes. It supports both PDF and DOCX formats and uses a plugin-based architecture for extensibility.

### What are the system requirements?

- Python 3.8 or higher
- Google API key for Gemini LLM
- Sufficient disk space for processing resumes
- Internet connection for API access

### What resume formats are supported?

Currently supported formats:
- PDF (.pdf)
- DOCX (.docx)

## Installation Issues

### Q: How do I install the tool?

A: Follow these steps:
1. Clone the repository
2. Create a virtual environment
3. Install dependencies
4. Configure environment variables
5. Create required directories

See the [Installation & Setup](Installation-and-Setup) guide for detailed instructions.

### Q: I'm getting dependency installation errors. What should I do?

A: Try these solutions:
1. Update pip: `python -m pip install --upgrade pip`
2. Install Visual C++ build tools (Windows)
3. Check Python version compatibility
4. Verify internet connection

### Q: How do I set up my Google API key?

A:
1. Get a Google API key from the Google Cloud Console
2. Copy `.env.example` to `.env`
3. Add your API key to the `GOOGLE_API_KEY` variable
4. Ensure the key has access to Gemini models

## Usage Questions

### Q: How do I process a single resume?

A: Use the `--resume` argument:
```bash
python main.py --resume path/to/resume.pdf
```

### Q: How do I process multiple resumes?

A: Place all resumes in the `Resumes/` directory and run:
```bash
python main.py
```

### Q: Where are the results saved?

A: Results are saved in the `Results/` directory as JSON files.

### Q: How do I view token usage?

A: Use the `--report-only` flag:
```bash
python main.py --resume example.pdf --report-only
```

## Plugin Questions

### Q: How do I create a custom plugin?

A: See the [Plugin System](Plugin-System) guide for detailed instructions.

### Q: Why isn't my plugin being loaded?

A: Check:
1. Plugin file is in the correct directory
2. Plugin is registered in `__init__.py`
3. Plugin implements all required methods
4. No syntax errors in plugin code

### Q: How do I debug a plugin?

A:
1. Enable debug logging in `.env`
2. Check plugin logs
3. Use print statements
4. Review error messages

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
2. Use a different API key
3. Reduce concurrent requests
4. Add delays between requests

### Processing Errors

#### Q: The tool isn't extracting information correctly. What's wrong?

A:
1. Check resume format and readability
2. Verify resume text extraction
3. Review plugin prompt templates
4. Check for OCR issues in scanned documents

#### Q: Processing is slow. How can I improve performance?

A:
1. Use concurrent processing
2. Optimize prompt templates
3. Implement caching
4. Reduce token usage

### File Issues

#### Q: The tool can't read my PDF file. What should I do?

A:
1. Check if the PDF is corrupted
2. Verify file permissions
3. Try converting to DOCX
4. Check PDF text extraction

#### Q: I'm getting "file not found" errors. How to fix?

A:
1. Verify file paths
2. Check directory permissions
3. Ensure files exist
4. Use absolute paths

## Logging and Debugging

### Q: How do I enable debug logging?

A: Set in `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Q: Where are the logs stored?

A: Logs are stored in:
- Main logs: `resume_analysis.log`
- Token usage: `logs/token_usage/`
- Debug logs: `logs/debug/`

### Q: How do I analyze token usage?

A:
1. Check token usage reports
2. Monitor API costs
3. Optimize prompts
4. Review usage patterns

## Security Questions

### Q: How do I secure my API key?

A:
1. Never commit `.env` file
2. Use environment variables
3. Rotate keys regularly
4. Restrict API access

### Q: How do I handle sensitive resume data?

A:
1. Implement data encryption
2. Use secure storage
3. Follow data protection guidelines
4. Clean up temporary files

## Performance Optimization

### Q: How can I reduce token usage?

A:
1. Optimize prompt templates
2. Implement text truncation
3. Use efficient models
4. Cache results

### Q: How do I improve processing speed?

A:
1. Use concurrent processing
2. Implement caching
3. Optimize file I/O
4. Reduce API calls

## Getting Help

### Q: Where can I get more help?

A:
1. Check the [User Guide](User-Guide)
2. Review the [Examples & Tutorials](Examples-and-Tutorials)
3. Join GitHub Discussions
4. Open an issue

### Q: How do I report a bug?

A:
1. Use the issue template
2. Provide detailed information
3. Include steps to reproduce
4. Add relevant logs

## Next Steps

- Review the [User Guide](User-Guide) for detailed usage instructions
- Check the [Examples & Tutorials](Examples-and-Tutorials) for practical examples
- Join the community for support and discussions
- Open an issue for unresolved problems 