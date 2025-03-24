# Contributing

Thank you for your interest in contributing to the Resume Analysis project! This guide will help you get started with contributing.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Understanding of the project's architecture

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/Resume-Analysis.git
   cd Resume-Analysis
   ```
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Development Guidelines

### Code Style

We follow PEP 8 guidelines and use Black for code formatting:

```bash
# Format code
black .

# Check code style
flake8
```

### Type Hints

- Use type hints for all function parameters and return values
- Use `typing` module for complex types
- Document type hints in docstrings

Example:
```python
from typing import List, Dict, Optional

def process_resume(
    text: str,
    plugins: List[BasePlugin]
) -> Dict[str, Any]:
    """
    Process resume text using specified plugins.
    
    Args:
        text: The resume text to process
        plugins: List of plugins to use
        
    Returns:
        Dictionary containing processed results
    """
    pass
```

### Testing

- Write unit tests for new features
- Maintain test coverage above 80%
- Use pytest for testing

Example test:
```python
import pytest
from resume_processor import ResumeProcessor

def test_process_resume():
    processor = ResumeProcessor()
    result = processor.process_resume_sync("test_resume.pdf")
    assert "name" in result
    assert "skills" in result
```

### Documentation

- Update documentation for new features
- Add docstrings to all functions and classes
- Keep README.md up to date
- Update wiki pages as needed

Example docstring:
```python
class ResumeProcessor:
    """
    Processes resumes using configured plugins.
    
    This class coordinates the processing of resumes using multiple plugins,
    handling concurrent execution and result aggregation.
    
    Attributes:
        plugins: List of plugins to use for processing
    """
```

## Pull Request Process

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes:
   - Write code
   - Add tests
   - Update documentation
   - Format code with Black

3. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a Pull Request:
   - Go to the project's GitHub page
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template

### Pull Request Template

```markdown
## Description
Brief description of your changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing performed

## Documentation
- [ ] README.md updated
- [ ] Wiki pages updated
- [ ] Code comments added

## Checklist
- [ ] Code follows PEP 8 style
- [ ] Type hints added
- [ ] Tests pass
- [ ] Documentation updated
```

## Plugin Development

### Creating New Plugins

1. Create a new file in `custom_plugins/`:
   ```python
   from base_plugins.base import BasePlugin
   
   class NewPlugin(BasePlugin):
       # Implement required methods
       pass
   ```

2. Add tests in `tests/test_custom_plugins/`:
   ```python
   def test_new_plugin():
       plugin = NewPlugin()
       result = plugin.process_output("test input")
       assert result is not None
   ```

3. Update documentation:
   - Add plugin description to wiki
   - Include usage examples
   - Document configuration options

### Plugin Guidelines

- Keep plugins focused and single-purpose
- Implement proper error handling
- Validate LLM outputs
- Optimize token usage
- Write comprehensive tests

## Code Review Process

1. **Initial Review**
   - Check code style
   - Verify tests
   - Review documentation

2. **Technical Review**
   - Architecture review
   - Performance considerations
   - Security implications

3. **Final Review**
   - Documentation completeness
   - Test coverage
   - Integration testing

## Release Process

1. **Version Bumping**
   - Update version in `__init__.py`
   - Update CHANGELOG.md
   - Tag release in Git

2. **Documentation**
   - Update release notes
   - Update wiki pages
   - Update API documentation

3. **Distribution**
   - Build distribution
   - Upload to PyPI
   - Create GitHub release

## Community Guidelines

### Communication

- Be respectful and professional
- Use clear and concise language
- Provide context for questions
- Follow up on discussions

### Issue Reporting

When reporting issues:

1. Use the issue template
2. Provide detailed information
3. Include steps to reproduce
4. Add relevant logs/screenshots

### Feature Requests

When requesting features:

1. Explain the problem
2. Describe the solution
3. Provide use cases
4. Consider alternatives

## Getting Help

- Check the [FAQ & Troubleshooting](FAQ-and-Troubleshooting) page
- Review the [Examples & Tutorials](Examples-and-Tutorials)
- Ask in GitHub Discussions
- Join the community chat

## Next Steps

- Review the [Technical Documentation](Technical-Documentation)
- Check out the [Plugin System](Plugin-System) guide
- Start with a small contribution
- Join the community discussions 