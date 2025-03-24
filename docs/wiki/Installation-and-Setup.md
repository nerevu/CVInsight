# Installation & Setup

This guide will help you set up the Resume Analysis tool on your system.

## System Requirements

- Python 3.8 or higher
- Google API key for Gemini LLM
- Sufficient disk space for processing resumes and storing results
- Internet connection for API access

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Resume-Analysis.git
cd Resume-Analysis
```

### 2. Set Up Virtual Environment

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your settings:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   DEFAULT_LLM_MODEL=gemini-2.0-flash
   RESUME_DIR=./Resumes
   OUTPUT_DIR=./Results
   LOG_LEVEL=INFO
   LOG_FILE=resume_analysis.log
   TOKEN_LOG_RETENTION_DAYS=7
   LOG_MAX_SIZE_MB=5
   LOG_BACKUP_COUNT=3
   DEBUG=False
   ```

### 5. Create Required Directories

```bash
mkdir Resumes
mkdir Results
mkdir logs
```

## Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_API_KEY` | Your Google API key for Gemini LLM | - | Yes |
| `DEFAULT_LLM_MODEL` | Model name to use | gemini-2.0-flash | No |
| `RESUME_DIR` | Directory containing resume files | ./Resumes | No |
| `OUTPUT_DIR` | Directory for processed results | ./Results | No |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | INFO | No |
| `LOG_FILE` | Path to log file | resume_analysis.log | No |
| `TOKEN_LOG_RETENTION_DAYS` | Days to keep token usage logs | 7 | No |
| `LOG_MAX_SIZE_MB` | Max size of log files before rotation | 5 | No |
| `LOG_BACKUP_COUNT` | Number of backup log files | 3 | No |
| `DEBUG` | Enable debug mode | False | No |

### Directory Structure

```
Resume-Analysis/
├── Resumes/           # Place your resume files here
├── Results/           # Processed results will be saved here
├── logs/             # Log files directory
├── base_plugins/     # Core plugin implementations
├── custom_plugins/   # User-defined plugins
├── models/          # Data models
├── utils/           # Utility functions
└── main.py          # Main application entry point
```

## Troubleshooting Common Issues

### 1. API Key Issues

- Ensure your Google API key is valid and has access to Gemini models
- Check if the API key is properly set in the `.env` file
- Verify there are no extra spaces or quotes around the API key

### 2. Virtual Environment Problems

- Make sure you're using the correct Python version
- Try recreating the virtual environment if dependencies aren't installing correctly
- Verify the virtual environment is activated before running commands

### 3. Permission Issues

- Ensure you have write permissions in the project directory
- Check if the logs and Results directories are writable
- Verify file permissions for resume files

### 4. Dependencies Installation

- If pip install fails, try updating pip: `python -m pip install --upgrade pip`
- For Windows users, some packages might require Visual C++ build tools
- Check the requirements.txt file for any platform-specific dependencies

## Next Steps

- Read the [User Guide](User-Guide) to learn how to use the tool
- Check out the [Examples & Tutorials](Examples-and-Tutorials) for practical usage
- Review the [Plugin System](Plugin-System) documentation if you want to extend functionality 