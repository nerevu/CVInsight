# User Guide

This guide will help you use the Resume Analysis tool effectively to process and analyze resumes.

## Basic Usage

### Processing Resumes

1. Place your resume files (PDF or DOCX) in the `Resumes/` directory
2. Run the main script:
   ```bash
   python main.py
   ```
3. Find the processed results in the `Results/` directory

### Command-Line Arguments

The tool supports various command-line arguments for different use cases:

```bash
# Process a single resume file
python main.py --resume example.pdf

# Display token usage report for a previously processed resume
python main.py --resume example.pdf --report-only

# Specify a custom directory for token usage logs
python main.py --log-dir ./custom_logs

# Enable verbose logging
python main.py --verbose

# Clean up __pycache__ directories and compiled Python files
python main.py --cleanup
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
  "resume_file": "John_Doe.pdf",
  "processed_at": "20250323_031534",
  "token_usage": {
    "total_tokens": 7695,
    "prompt_tokens": 7410,
    "completion_tokens": 285,
    "by_extractor": {
      "ProfileExtractorPlugin": {
        "total_tokens": 1445,
        "prompt_tokens": 1423,
        "completion_tokens": 22
      },
      "SkillsExtractorPlugin": {
        "total_tokens": 1383,
        "prompt_tokens": 1304,
        "completion_tokens": 79
      },
      "EducationExtractorPlugin": {
        "total_tokens": 1672,
        "prompt_tokens": 1624,
        "completion_tokens": 48
      },
      "ExperienceExtractorPlugin": {
        "total_tokens": 1704,
        "prompt_tokens": 1586,
        "completion_tokens": 118
      },
      "YoeExtractorPlugin": {
        "total_tokens": 1491,
        "prompt_tokens": 1473,
        "completion_tokens": 18
      }
    }
  }
}
```

## Advanced Features

### Batch Processing

To process multiple resumes efficiently:

1. Place all resumes in the `Resumes/` directory
2. Run the main script without arguments:
   ```bash
   python main.py
   ```
3. The tool will process all resumes concurrently and generate results in the `Results/` directory

### Token Usage Optimization

To optimize token usage:

1. Monitor token usage reports in the `logs/token_usage` directory
2. Adjust prompt templates in plugins if needed
3. Use the `--report-only` flag to analyze token usage without reprocessing

### Log Management

The system provides comprehensive logging:

- Main application logs in `resume_analysis.log`
- Token usage logs in `logs/token_usage/`
- Debug logs when `DEBUG=True` in `.env`

Logs are automatically rotated based on size and retention settings in `.env`.

## Best Practices

1. **Resume Format**
   - Use PDF or DOCX format for best results
   - Ensure resumes are properly formatted and readable
   - Avoid scanned documents or images

2. **Performance**
   - Process resumes in batches for better efficiency
   - Monitor token usage to optimize costs
   - Clean up old logs regularly

3. **Error Handling**
   - Check logs for processing errors
   - Verify API key validity
   - Ensure sufficient disk space

4. **Security**
   - Keep API keys secure
   - Regularly rotate API keys
   - Don't share processed results containing sensitive information

## Troubleshooting

### Common Issues

1. **API Errors**
   - Check API key validity
   - Verify internet connection
   - Monitor API rate limits

2. **Processing Failures**
   - Check resume file format
   - Verify file permissions
   - Review error logs

3. **Token Usage Issues**
   - Monitor token usage reports
   - Check prompt templates
   - Verify API quota

### Getting Help

- Check the [FAQ & Troubleshooting](FAQ-and-Troubleshooting) page
- Review the [Examples & Tutorials](Examples-and-Tutorials)
- Open an issue on GitHub for bugs or feature requests 