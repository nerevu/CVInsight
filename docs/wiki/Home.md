# Resume Analysis Wiki

Welcome to the Resume Analysis project wiki! This documentation will help you understand, set up, and use the Resume Analysis tool effectively.

## Overview

Resume Analysis is a powerful Python-based application designed to streamline the resume review process. It automatically extracts and analyzes information from PDF and DOCX resumes using Google's Gemini Large Language Models (LLMs). The system features a flexible plugin architecture that makes it easy to extend its functionality.

## Key Features

- **Plugin-Based Architecture**: Extend functionality by adding new plugins
- **Multiple Resume Formats**: Support for PDF and DOCX files
- **Comprehensive Information Extraction**:
  - Basic profile information
  - Skills analysis
  - Education history
  - Work experience
  - Years of experience calculation
- **Efficient Processing**:
  - Concurrent processing of multiple aspects
  - Structured JSON output
  - Token usage tracking and optimization
- **Robust Logging**:
  - Separate log files for different purposes
  - Automatic log rotation
  - Configurable log retention

## Quick Start

1. Clone the repository
2. Set up your environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```
3. Configure your environment:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferences
   ```
4. Process resumes:
   ```bash
   python main.py
   ```

## Documentation Sections

- [Installation & Setup](Installation-and-Setup) - Detailed setup instructions
- [User Guide](User-Guide) - How to use the tool effectively
- [Plugin System](Plugin-System) - Understanding and extending the plugin architecture
- [Technical Documentation](Technical-Documentation) - Internal implementation details
- [Examples & Tutorials](Examples-and-Tutorials) - Practical usage examples
- [Contributing](Contributing) - How to contribute to the project
- [FAQ & Troubleshooting](FAQ-and-Troubleshooting) - Common issues and solutions

## Getting Help

- Check the [FAQ & Troubleshooting](FAQ-and-Troubleshooting) page for common issues
- Review the [Examples & Tutorials](Examples-and-Tutorials) for usage patterns
- Open an issue on GitHub for bug reports or feature requests
- Join our community discussions

## License

This project is licensed under the MIT License - see the LICENSE file for details. 