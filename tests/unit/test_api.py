"""Test the main API functions."""
import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path so we can import cvinsight
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from cvinsight import api


class TestAPI:
    """Test the API module functions."""
    
    @pytest.fixture
    def mock_processor(self):
        """Mock processor for testing."""
        with patch('cvinsight.api._get_processor') as mock:
            yield mock.return_value
    
    @pytest.fixture
    def mock_plugin_manager(self):
        """Mock plugin manager for testing."""
        with patch('cvinsight.api._get_plugin_manager') as mock:
            yield mock.return_value
    
    def test_configure(self):
        """Test API configuration."""
        with patch('cvinsight.api._get_llm_service'), \
             patch('cvinsight.api._get_plugin_manager'), \
             patch('cvinsight.api._get_processor'):
            
            api.configure("test-api-key", "test-model")
            
            # Should not raise any exceptions
            assert True
    
    def test_extract_all(self, mock_processor):
        """Test extract_all function."""
        mock_resume = Mock()
        mock_resume.model_dump.return_value = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python"]
        }
        # Make token_usage JSON serializable
        mock_resume.token_usage = {"input_tokens": 100, "output_tokens": 50}
        mock_processor.process_resume.return_value = mock_resume
        
        result = api.extract_all("fake_resume.pdf")
        
        assert isinstance(result, dict)
        assert "name" in result
        mock_processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_extract_profile(self, mock_processor):
        """Test extract_profile function."""
        mock_result = Mock()
        mock_result.profile = {"name": "John Doe", "email": "john@example.com"}
        mock_processor.process_resume.return_value = mock_result
        
        result = api.extract_profile("fake_resume.pdf")
        
        assert isinstance(result, dict)
        mock_processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_extract_education(self, mock_processor):
        """Test extract_education function."""
        # Create proper education objects with model_dump method
        education1 = Mock()
        education1.model_dump.return_value = {"degree": "Bachelor of Science", "institution": "Test University"}
        
        mock_result = Mock()
        mock_result.educations = [education1]
        mock_processor.process_resume.return_value = mock_result
        
        result = api.extract_education("fake_resume.pdf")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["degree"] == "Bachelor of Science"
        mock_processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_extract_experience(self, mock_processor):
        """Test extract_experience function."""
        # Create proper experience objects with model_dump method
        experience1 = Mock()
        experience1.model_dump.return_value = {"title": "Software Engineer", "company": "Tech Corp"}
        
        mock_result = Mock()
        mock_result.work_experiences = [experience1]
        mock_processor.process_resume.return_value = mock_result
        
        result = api.extract_experience("fake_resume.pdf")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Software Engineer"
        mock_processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_extract_skills(self, mock_processor):
        """Test extract_skills function."""
        mock_result = Mock()
        mock_result.skills = ["Python", "Machine Learning"]
        mock_processor.process_resume.return_value = mock_result
        
        result = api.extract_skills("fake_resume.pdf")
        
        assert isinstance(result, dict)
        assert "skills" in result
        mock_processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_extract_years_of_experience(self, mock_processor):
        """Test extract_years_of_experience function."""
        mock_result = Mock()
        mock_result.YoE = "3.5"  # Use the correct attribute name from the API implementation
        mock_processor.process_resume.return_value = mock_result
        
        result = api.extract_years_of_experience("fake_resume.pdf")
        
        assert result == "3.5"
        mock_processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_list_all_plugins(self, mock_plugin_manager):
        """Test list_all_plugins function."""
        mock_plugins = [
            {"name": "profile_extractor", "version": "1.0.0"},
            {"name": "skills_extractor", "version": "1.0.0"}
        ]
        mock_plugin_manager.list_plugins.return_value = mock_plugins
        
        result = api.list_all_plugins()
        
        assert isinstance(result, list)
        assert len(result) == 2
        mock_plugin_manager.list_plugins.assert_called_once()
    
    def test_list_plugins_by_category(self, mock_plugin_manager):
        """Test list_plugins_by_category function."""
        mock_plugins = [
            {"name": "profile_extractor", "category": "base"}
        ]
        mock_plugin_manager.list_plugins_by_category.return_value = mock_plugins
        
        result = api.list_plugins_by_category("base")
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_plugin_manager.list_plugins_by_category.assert_called_once_with("base")
    
    def test_analyze_resume(self, mock_processor):
        """Test analyze_resume function."""
        mock_result = {"status": "success", "data": {"name": "John Doe"}}
        mock_processor.process_resume.return_value = mock_result
        
        result = api.analyze_resume("fake_resume.pdf")
        
        assert isinstance(result, dict)
        mock_processor.process_resume.assert_called_once_with("fake_resume.pdf")
