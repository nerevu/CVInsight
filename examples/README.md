# CVInsight Examples

This directory contains production-ready examples demonstrating CVInsight's unified resume analysis capabilities.

## 📚 Available Examples

### Core Examples
These examples demonstrate different aspects of CVInsight's capabilities:

### 🎯 **minimal_cvinsight.ipynb** 
**Job Description Comparison Demo** - The main example showcasing CVInsight's power:
- Compare candidate suitability across different job roles (Data Analyst vs Florist)
- Demonstrates job-specific relevance scoring
- Shows how the same resume scores differently for different positions
- Real-world application of unified extractor performance

### 🚀 **unified_extractor_demo.ipynb**
**Performance Demonstration** - Technical showcase of the unified extractor:
- 75% performance improvement demonstration
- Side-by-side comparison of old vs new architecture
- Token usage and cost analysis
- Complete system validation

### 🎬 **final_unified_demo.py**
**Command-Line Demo Script** - Production demo script:
- Complete end-to-end workflow demonstration
- Performance benchmarking
- System health validation
- Ready-to-run integration test

---

### Integration Examples
**NEW!** Three distinct examples showing how to integrate CVInsight from external repositories:

### 🏭 **production_batch_processor.py**
**Enterprise Production Script** - Full-featured batch processor for production use:
- Command-line interface with configurable parameters
- Production-grade logging and error handling
- Performance metrics and reporting
- Structured CSV/JSON output
- Integration patterns for external repositories
- Complete error recovery workflows

### ⚡ **concurrent_analysis_demo.ipynb**
**High-Performance Concurrent Processing** - Advanced parallel processing demonstration:
- Performance benchmarking (parallel vs sequential)
- Scalability testing with different batch sizes
- Real-time performance visualization
- Advanced candidate ranking and analysis
- Speedup calculations and optimization techniques
- Export capabilities for downstream systems

### 📖 **step_by_step_tutorial.ipynb**
**Educational Walkthrough** - Comprehensive learning tutorial:
- 10-step sequential learning process
- Detailed explanations of all 21 unified extractor fields
- Job relevance scoring methodology
- No parallel processing for clarity
- Integration examples and best practices
- Complete results interpretation guidance

## 🚀 Quick Start

### Prerequisites
```bash
# Set your OpenAI API key
export OPEN_AI_API_KEY="your-api-key-here"

# Install CVInsight (if not already installed)
pip install -e /path/to/CVInsight
```

### Basic Usage
```python
from cvinsight.notebook_utils import initialize_client, parse_single_resume

# Initialize
client = initialize_client("your-api-key")

# Parse a resume with job context
result = parse_single_resume(
    client=client,
    resume_path="path/to/resume.pdf",
    date_of_resume_submission="2025-05-29",
    job_description="Your job description here"
)
```

## 🎯 Key Features Demonstrated

### Performance Optimization
- **75% faster processing** with unified extractor
- **Single API call** for comprehensive analysis
- **21 structured fields** extracted efficiently

### Job-Specific Analysis
- **Dynamic relevance scoring** based on job requirements
- **Context-aware experience evaluation**
- **Education relevance assessment**

### Production Features
- **Error handling and recovery**
- **Parallel processing capabilities**
- **Comprehensive logging and monitoring**

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
