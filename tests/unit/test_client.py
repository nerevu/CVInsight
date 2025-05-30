"""Test CVInsightClient functionality."""
import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock, mock_open

# Add the parent directory to the path so we can import cvinsight
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from cvinsight import CVInsightClient
from cvinsight.client import CVInsightClient as DirectClient


class TestCVInsightClient:
    """Test the CVInsightClient class."""
    
    @pytest.fixture
    def mock_api_key(self):
        return "test-api-key-12345"
    
    @pytest.fixture
    def client(self, mock_api_key):
        """Create a test client instance."""
        with patch('cvinsight.client.LLMService'), \
             patch('cvinsight.client.PluginManager'), \
             patch('cvinsight.client.ResumeProcessor'):
            return CVInsightClient(api_key=mock_api_key, provider="google")
    
    def test_client_initialization_google(self, mock_api_key):
        """Test client initialization with Google provider."""
        with patch('cvinsight.client.LLMService') as mock_llm, \
             patch('cvinsight.client.PluginManager') as mock_pm, \
             patch('cvinsight.client.ResumeProcessor') as mock_rp:
            
            client = CVInsightClient(api_key=mock_api_key, provider="google")
            
            # Check that API key was set in environment
            assert os.environ.get("GOOGLE_API_KEY") == mock_api_key
            
            # Check that services were initialized
            mock_llm.assert_called_once()
            mock_pm.assert_called_once()
            mock_rp.assert_called_once()
    
    def test_client_initialization_openai(self, mock_api_key):
        """Test client initialization with OpenAI provider."""
        with patch('cvinsight.client.LLMService') as mock_llm, \
             patch('cvinsight.client.PluginManager') as mock_pm, \
             patch('cvinsight.client.ResumeProcessor') as mock_rp:
            
            client = CVInsightClient(api_key=mock_api_key, provider="openai")
            
            # Check that API key was set in environment
            assert os.environ.get("OPENAI_API_KEY") == mock_api_key
    
    def test_extract_all(self, client):
        """Test extract_all method."""
        mock_resume = Mock()
        mock_resume.model_dump.return_value = {
            "name": "John Doe", 
            "email": "john@example.com",
            "skills": ["Python", "Machine Learning"]
        }
        mock_resume.token_usage = {"total_tokens": 100}  # Make it serializable
        
        client._processor.process_resume.return_value = mock_resume
        
        # Mock file operations
        with patch('builtins.open'), \
             patch('json.dump'), \
             patch('os.makedirs'):
            
            result = client.extract_all("fake_resume.pdf")
            
            assert isinstance(result, dict)
            assert "name" in result
            assert "email" in result
            assert "skills" in result
            client._processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_extract_profile(self, client):
        """Test extract_profile method."""
        mock_result = Mock()
        mock_result.profile = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "123-456-7890"
        }
        
        client._processor.process_resume.return_value = mock_result
        
        result = client.extract_profile("fake_resume.pdf")
        
        assert isinstance(result, dict)
        assert "name" in result or "profile" in result
        client._processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_extract_education(self, client):
        """Test extract_education method."""
        mock_result = Mock()
        # Create mock education objects with model_dump method
        mock_edu1 = Mock()
        mock_edu1.model_dump.return_value = {"degree": "Bachelor of Science", "institution": "Test University"}
        mock_edu2 = Mock()
        mock_edu2.model_dump.return_value = {"degree": "Master of Arts", "institution": "Another University"}
        
        mock_result.educations = [mock_edu1, mock_edu2]
        
        client._processor.process_resume.return_value = mock_result
        
        result = client.extract_education("fake_resume.pdf")
        
        assert isinstance(result, list)
        client._processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_extract_experience(self, client):
        """Test extract_experience method."""
        mock_result = Mock()
        # Create mock experience objects with model_dump method
        mock_exp1 = Mock()
        mock_exp1.model_dump.return_value = {"title": "Software Engineer", "company": "Tech Corp"}
        mock_exp2 = Mock()
        mock_exp2.model_dump.return_value = {"title": "Data Analyst", "company": "Data Inc"}
        
        mock_result.work_experiences = [mock_exp1, mock_exp2]
        
        client._processor.process_resume.return_value = mock_result
        
        result = client.extract_experience("fake_resume.pdf")
        
        assert isinstance(result, list)
        client._processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_extract_skills(self, client):
        """Test extract_skills method."""
        mock_result = Mock()
        mock_result.skills = ["Python", "Machine Learning", "Data Analysis"]
        
        client._processor.process_resume.return_value = mock_result
        
        result = client.extract_skills("fake_resume.pdf")
        
        assert isinstance(result, dict)
        assert "skills" in result
        client._processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_extract_years_of_experience(self, client):
        """Test extract_years_of_experience method."""
        mock_result = Mock()
        mock_result.YoE = "5.2"  # Note: the actual property is 'YoE' not 'years_of_experience'
        
        client._processor.process_resume.return_value = mock_result
        
        result = client.extract_years_of_experience("fake_resume.pdf")
        
        assert result == "5.2"
        client._processor.process_resume.assert_called_once_with("fake_resume.pdf")
    
    def test_list_all_plugins(self, client):
        """Test list_all_plugins method."""
        mock_plugins = [
            {"name": "profile_extractor", "version": "1.0.0"},
            {"name": "skills_extractor", "version": "1.0.0"}
        ]
        client._plugin_manager.list_plugins.return_value = mock_plugins
        
        result = client.list_all_plugins()
        
        assert isinstance(result, list)
        assert len(result) == 2
        client._plugin_manager.list_plugins.assert_called_once()
    
    def test_list_plugins_by_category(self, client):
        """Test list_plugins_by_category method."""
        mock_plugins = [
            {"name": "profile_extractor", "category": "base"},
        ]
        client._plugin_manager.list_plugins_by_category.return_value = mock_plugins
        
        result = client.list_plugins_by_category("base")
        
        assert isinstance(result, list)
        assert len(result) == 1
        client._plugin_manager.list_plugins_by_category.assert_called_once_with("base")
    
    def test_analyze_resume(self, client):
        """Test analyze_resume method."""
        mock_result = {"status": "success", "data": {"name": "John Doe"}}
        
        # Mock the API function that analyze_resume delegates to
        with patch('cvinsight.api.analyze_resume') as mock_api_call:
            mock_api_call.return_value = mock_result
            
            result = client.analyze_resume("fake_resume.pdf")
            
            assert isinstance(result, dict)
            mock_api_call.assert_called_once_with("fake_resume.pdf", None, True)
