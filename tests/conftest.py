"""Shared fixtures for CVInsight tests."""
import os
import pytest
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def sample_resume_path(temp_dir: Path) -> Path:
    """Create a sample resume file for testing."""
    resume_path = temp_dir / "sample_resume.pdf"
    # Create an empty file for now
    resume_path.touch()
    return resume_path

@pytest.fixture
def sample_resume_text() -> str:
    """Return a sample resume text for testing."""
    return """
    JOHN DOE
    Software Engineer
    john.doe@email.com | (555) 123-4567
    
    SUMMARY
    Experienced software engineer with 5+ years of experience in Python and web development.
    
    SKILLS
    - Python, JavaScript, SQL
    - Django, Flask, FastAPI
    - AWS, Docker, Kubernetes
    - Git, CI/CD
    
    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2020-Present
    - Led development of microservices architecture
    - Implemented CI/CD pipelines
    
    Software Engineer | StartUp Inc | 2018-2020
    - Developed full-stack web applications
    - Optimized database queries
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology | 2014-2018
    """

@pytest.fixture
def sample_resume_data() -> Dict[str, Any]:
    """Return sample resume data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "(555) 123-4567",
        "title": "Software Engineer",
        "skills": ["Python", "JavaScript", "SQL", "Django", "Flask", "FastAPI", "AWS", "Docker", "Kubernetes", "Git", "CI/CD"],
        "work_experiences": [
            {
                "company": "Tech Corp",
                "role": "Senior Software Engineer",
                "duration": "2020-Present",
                "description": ["Led development of microservices architecture", "Implemented CI/CD pipelines"]
            },
            {
                "company": "StartUp Inc",
                "role": "Software Engineer",
                "duration": "2018-2020",
                "description": ["Developed full-stack web applications", "Optimized database queries"]
            }
        ],
        "educations": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Technology",
                "duration": "2014-2018"
            }
        ]
    }

@pytest.fixture
def mock_plugin_manager(mocker):
    """Create a mock plugin manager for testing."""
    from cvinsight.base_plugins.plugin_manager import PluginManager
    mock_manager = mocker.Mock(spec=PluginManager)
    mock_manager.plugins = {}
    return mock_manager

@pytest.fixture
def mock_processor(mocker):
    """Create a mock resume processor for testing."""
    from cvinsight.core.resume_processor import PluginResumeProcessor
    mock_processor = mocker.Mock(spec=PluginResumeProcessor)
    return mock_processor 