# CVInsight Test Scripts

This directory contains test scripts for testing the CVInsight resume parsing system.

## Available Test Scripts

### 1. test_custom_plugins.py

This script tests the custom plugins directly on a single resume file. It helps verify that each plugin works correctly in isolation.

**Usage:**
```bash
python test_custom_plugins.py
```

### 2. test_plugin_integration.py

This script tests the integration of custom plugins with the CVInsight client. It ensures that custom plugin data is correctly extracted and accessible through the client interface.

**Usage:**
```bash
python test_plugin_integration.py
```

### 3. compare_results.py

This utility script compares extraction results between different runs of the system. It's useful for validating that optimizations maintain extraction quality.

**Usage:**
```bash
python compare_results.py
```

### 4. test_full_dataset.py

Comprehensive test that runs the CVInsight parser on all available resumes with detailed metrics collection.

**Usage:**
```bash
# Run with default settings
python test_full_dataset.py

# Run with limited number of resumes
python test_full_dataset.py --limit 10

# Use a specific model
python test_full_dataset.py --model "gpt-3.5-turbo"

# Specify output directory
python test_full_dataset.py --output "Results/full_test"
```

### 5. analyze_performance.py

Analyzes performance metrics from test results, generating visualizations and comparisons.

**Usage:**
```bash
# Run with default results file
python analyze_performance.py

# Specify a specific results file
python analyze_performance.py --results "Results/custom_results.csv"

# Compare with a baseline for improvement metrics
python analyze_performance.py --baseline "Results/baseline_results.csv"
```

### 6. performance_monitor.py

Provides detailed analysis of resume parsing results with advanced visualizations.

**Usage:**
```bash
# Run with default settings
python performance_monitor.py

# Specify input and output locations
python performance_monitor.py --input Results/custom_results.csv --output Results/performance_analysis
```

### 7. compare_performance.py

Compares two different runs of the CVInsight system to measure improvements over time.

**Usage:**
```bash
# Compare baseline with current results
python compare_performance.py --baseline Results/baseline_results.csv --current Results/current_results.csv

# Specify output directory
python compare_performance.py --baseline Results/baseline_results.csv --current Results/current_results.csv --output Results/comparisons
```

## Running Tests from the Root Directory

You can also run the tests from the project root directory:

```bash
python -m tests.scripts.test_custom_plugins
python -m tests.scripts.test_plugin_integration
python -m tests.scripts.compare_results
python -m tests.scripts.test_full_dataset
python -m tests.scripts.analyze_performance
```

## Prerequisites

- Make sure you have set up a `.env` file with your OpenAI API key (`OPEN_AI_API_KEY`)
- Ensure you have at least one resume file in the `Resumes` directory
- Run the main script at least once to generate result files before running `compare_results.py`
- For performance analysis scripts, matplotlib is required (`pip install matplotlib`)

## Output

Most scripts save their output to the `Results` directory in the project root:

- CSV files with parsed resume data
- Log files with detailed execution information
- Performance metrics and visualizations
- Comparison reports
