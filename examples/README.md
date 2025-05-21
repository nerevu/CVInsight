# CVInsight Jupyter Notebook Examples

This directory contains example Jupyter notebooks demonstrating how to use the CVInsight resume parsing system in your own projects.

## Available Examples

1. **cvinsight_demo.ipynb** - A comprehensive demonstration of all CVInsight notebook utilities
2. **target_notebook_integration.ipynb** - A specific integration example for the Resume Parser project
3. **robust_notebook_integration.ipynb** - An error-resistant implementation with advanced features
4. **cvinsight_quick_start.ipynb** - A clean, step-by-step guide to using the core functions
5. **minimal_cvinsight.ipynb** - Super slim implementation with minimal boilerplate

## How to Use These Examples

### Prerequisites

1. Ensure you have the CVInsight repository available on your machine
2. Set up your environment with the necessary API keys:
   - OpenAI API key (`OPEN_AI_API_KEY`)
   - Google Gemini API key (`GEMINI_API_KEY`) 
3. Have resume files available (PDF, DOC, or DOCX format)

### Running the Examples

1. Open the example notebook in Jupyter Lab or VS Code
2. Update the paths to match your environment:
   - Update `cvinsight_path` to point to your CVInsight repository
   - Update resume directory paths to point to your resume files
3. Run the cells in sequence to see how the CVInsight utilities work

## Key Components

The CVInsight notebook utilities provide the following functions:

- `initialize_client(api_key, provider, model_name)` - Initialize the CVInsight client with all plugins
- `parse_single_resume(client, resume_path, date_of_resume_submission, job_description)` - Parse a single resume and return the extracted information
- `parse_many_resumes(client, resume_paths, date_of_resume_submission, job_description, use_tqdm, parallel, max_workers)` - Parse multiple resumes with optional parallel processing
- `find_resumes(directory_path)` - Find all resume files in a directory

## Integration Tips

When integrating CVInsight into your own projects:

1. Ensure the CVInsight repository is in your Python path
2. Use the `initialize_client()` function for consistent setup with all plugins
3. For large batches of resumes, enable parallel processing with `parse_many_resumes(parallel=True)`
4. Handle errors gracefully by checking the `parsing_status` field in the results

## Further Customization

You can customize the parsing behavior by:

1. Selecting specific LLM providers and models
2. Using parallel processing for large datasets
3. Implementing custom post-processing of the DataFrame results

For more details on customization options, see the [CVInsight documentation](../../README.md).
