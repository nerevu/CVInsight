# Installation & Setup

This guide will help you set up and configure the CVInsight package on your system.

## System Requirements

- Python 3.9 or higher
- Google API key for Gemini LLM
- Sufficient disk space for processing resumes and storing results
- Internet connection for API access

## Installation Options

### Option 1: Install from PyPI (Recommended)

The simplest way to install CVInsight is directly from PyPI:

```bash
pip install cvinsight
```

This will install the package and all its dependencies.

### Option 2: Install from Source

If you want to install from source (e.g., for development):

```bash
# Clone the repository
git clone https://github.com/Gaurav-Kumar98/CVInsight.git
cd CVInsight

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install in development mode
pip install -e .
```

## API Key Setup

CVInsight requires a Google API key to access the Gemini models:

1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Sign in with your Google account
3. Navigate to the "Get API key" option
4. Create a new API key

You can provide the API key in several ways:

1. Directly to the client:
   ```python
   from cvinsight import CVInsightClient
   client = CVInsightClient(api_key="your_google_api_key")
   ```

2. Set as environment variable:
   ```bash
   # Linux/Mac
   export GOOGLE_API_KEY=your_google_api_key
   
   # Windows (Command Prompt)
   set GOOGLE_API_KEY=your_google_api_key
   
   # Windows (PowerShell)
   $env:GOOGLE_API_KEY="your_google_api_key"
   ```

## Directory Structure

When using CVInsight as a package, the default directory structure is:

```
your_project/
├── logs/             # Token usage logs will be saved here (created automatically)
└── your_script.py    # Your Python script using CVInsight
```

For the command-line interface:

```
your_project/
├── Resumes/          # Place your resume files here
├── Results/          # Processed results will be saved here
├── logs/             # Token usage logs will be saved here
└── (Other files)
```

## Configuration Options

### Client Configuration

You can configure the CVInsight client in your code:

```python
from cvinsight import CVInsightClient

# Initialize with custom model
client = CVInsightClient(
    api_key="your_google_api_key",  # Optional if set as environment variable
    model_name="gemini-2.0-flash"   # Optional, uses default if not specified
)
```

### Command-Line Options

The CVInsight CLI offers several options:

```bash
# Process a single resume file
cvinsight --resume example.pdf

# Specify output directory
cvinsight --resume example.pdf --output ./results

# List available plugins
cvinsight --list-plugins

# Use specific plugins
cvinsight --resume example.pdf --plugins profile_extractor,skills_extractor

# Output as JSON
cvinsight --resume example.pdf --json
```

## Free Tier Limitations

Google offers a generous free tier for the Gemini API:

- **Cost**: Input and output tokens are completely free on the free tier
- **Models**: Access to models like Gemini 1.5 Flash and Gemini 2.0 Flash
- **Rate Limits**:
  - 15 requests per minute (RPM)
  - 1,000,000 tokens per minute (TPM)
  - 1,500 requests per day (RPD)

For the CVInsight package, these limits translate to:
- **Maximum ~130 resumes per minute** within the token limit
- **Up to 1,500 resumes per day** due to the daily request limit

This is adequate for personal use, small businesses, or even medium-sized recruiting operations.

## Troubleshooting Common Issues

### 1. API Key Issues

- Ensure your Google API key is valid and has access to Gemini models
- Verify there are no extra spaces or quotes around the API key
- Try using the key directly in the client constructor

### 2. Installation Problems

- Make sure you're using Python 3.9 or higher
- Try upgrading pip: `python -m pip install --upgrade pip`
- Check if all dependencies were installed correctly

### 3. Permission Issues

- Ensure you have write permissions in the project directory
- Check if the logs directory is writable

### 4. Import Errors

- Verify that the package was installed correctly
- Make sure you're using the correct import statements

## Next Steps

- Read the [User Guide](User-Guide) to learn how to use the package
- Check out the [Examples & Tutorials](Examples-and-Tutorials) for practical usage
- Review the [Plugin System](Plugin-System) documentation if you want to extend functionality 