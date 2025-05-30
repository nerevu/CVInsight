"""Integration tests for the complete CVInsight system."""
import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch
import json

# Add the parent directory to the path so we can import cvinsight
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from cvinsight import CVInsightClient
from cvinsight.notebook_utils import initialize_client, parse_single_resume


class TestCVInsightIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def sample_resume_content(self):
        """Sample resume content for testing."""
        return """
        John Doe
        Software Engineer
        Email: john.doe@example.com
        Phone: (213) 555-1234
        
        Education:
        Master of Science in Computer Science
        University of California, Los Angeles (2018-2020)
        
        Bachelor of Science in Computer Science  
        University of California, San Diego (2014-2018)
        
        Experience:
        Senior Software Engineer at Google (2020-2023)
        - Developed machine learning algorithms
        - Led a team of 5 engineers
        
        Software Engineer at Microsoft (2018-2020)
        - Built web applications using React and Node.js
        - Implemented RESTful APIs
        
        Skills:
        Python, JavaScript, React, Node.js, Machine Learning, Docker, Kubernetes
        """
    
    @pytest.fixture
    def temp_resume_file(self, sample_resume_content):
        """Create a temporary resume file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_resume_content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_client_full_workflow(self, temp_resume_file):
        """Test the complete client workflow."""
        with patch('cvinsight.client.LLMService') as mock_llm, \
             patch('cvinsight.client.PluginManager') as mock_pm, \
             patch('cvinsight.client.ResumeProcessor') as mock_rp:
            
            # Setup mocks
            mock_resume = Mock()
            mock_resume.model_dump.return_value = {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "skills": ["Python", "JavaScript", "Machine Learning"],
                "educations": [
                    {"degree": "Master of Science in Computer Science", "institution": "UCLA"}
                ],
                "work_experiences": [
                    {"title": "Senior Software Engineer", "company": "Google"}
                ],
                "years_of_experience": "5.0"
            }
            # Make token_usage JSON serializable
            mock_resume.token_usage = {
                "total_tokens": 1500,
                "input_tokens": 1000,
                "output_tokens": 500
            }
            
            mock_processor = Mock()
            mock_processor.process_resume.return_value = mock_resume
            mock_rp.return_value = mock_processor
            
            # Test client initialization and extraction
            client = CVInsightClient(api_key="test-key")
            result = client.extract_all(temp_resume_file)
            
            assert isinstance(result, dict)
            assert "name" in result
            assert "email" in result
            assert "skills" in result
    
    def test_notebook_utils_integration(self, temp_resume_file):
        """Test notebook utilities integration."""
        with patch('cvinsight.notebook_utils.CVInsightClient') as mock_client_class, \
             patch('cvinsight.notebook_utils.ExtendedAnalysisExtractorPlugin'), \
             patch('cvinsight.core.utils.file_utils.read_file', return_value="Test resume content"):
            
            # Setup mock client
            mock_client = Mock()
            mock_client._llm_service = Mock()
            mock_client._plugin_manager = Mock()
            mock_client._plugin_manager.plugins = {}
            mock_client._plugin_manager.extractors = {}
            
            # Mock profile extractor
            mock_profile_extractor = Mock()
            mock_profile_extractor.extract.return_value = ({
                "name": "John Doe",
                "email": "john.doe@example.com",
                "contact_number": "555-123-4567"
            }, {})
            mock_client._plugin_manager.extractors['profile_extractor'] = mock_profile_extractor
            
            # Mock skills extractor
            mock_skills_extractor = Mock()
            mock_skills_extractor.extract.return_value = ({"skills": ["Python", "Java"]}, {})
            mock_client._plugin_manager.extractors['skills_extractor'] = mock_skills_extractor
            
            # Mock education extractor
            mock_education_extractor = Mock()
            mock_education_extractor.extract.return_value = ({"educations": []}, {})
            mock_client._plugin_manager.extractors['education_extractor'] = mock_education_extractor
            
            # Mock experience extractor
            mock_experience_extractor = Mock()
            mock_experience_extractor.extract.return_value = ({"work_experiences": []}, {})
            mock_client._plugin_manager.extractors['experience_extractor'] = mock_experience_extractor
            
            # Mock extended analysis extractor with comprehensive fields
            mock_extended_extractor = Mock()
            mock_extended_extractor.extract.return_value = ({
                "all_wyoe": 5.0,
                "all_relevant_wyoe": 4.0,
                "all_eyoe": 6.0,
                "relevant_eyoe": 6.0,
                "highest_degree": "Bachelor",
                "highest_degree_status": "completed",
                "highest_degree_major": "Computer Science",
                "highest_degree_school_prestige": "medium",
                "highest_seniority_level": "mid",
                "primary_position_title": "Software Engineer",
                "average_tenure_at_company_years": 2.0,
                "phone_number": "555-123-4567",
                "linkedin_url": "",
                "github_url": "",
                "portfolio_url": "",
                "twitter_url": "",
                "personal_website_url": "",
                "other_social_media_urls": [],
                "location": "",
                "additional_contact_info": ""
            }, {})
            mock_client._plugin_manager.extractors['extended_analysis_extractor'] = mock_extended_extractor
            
            # Mock YoE extractor
            mock_yoe_extractor = Mock()
            mock_yoe_extractor.extract.return_value = ({"YoE": "5 years"}, {})
            mock_client._plugin_manager.extractors['yoe_extractor'] = mock_yoe_extractor
            mock_client_class.return_value = mock_client
            
            # Test initialization
            client = initialize_client("test-api-key")
            assert client == mock_client
            
            # Test single resume parsing
            result = parse_single_resume(
                client=client,
                resume_path=temp_resume_file,
                job_description="Software Engineer position"
            )
            
            assert isinstance(result, dict)
            assert result["parsing_status"] == "success"
            assert "name" in result
    
    def test_plugin_system_integration(self):
        """Test plugin system integration."""
        with patch('cvinsight.client.LLMService') as mock_llm, \
             patch('cvinsight.client.PluginManager') as mock_pm, \
             patch('cvinsight.client.ResumeProcessor') as mock_rp:
            
            # Setup mock plugin manager
            mock_plugin_manager = Mock()
            mock_plugin_manager.list_plugins.return_value = [
                {"name": "profile_extractor", "version": "1.0.0", "category": "base"},
                {"name": "extended_analysis_extractor", "version": "1.0.0", "category": "custom"}
            ]
            mock_pm.return_value = mock_plugin_manager
            
            client = CVInsightClient(api_key="test-key")
            plugins = client.list_all_plugins()
            
            assert isinstance(plugins, list)
            assert len(plugins) == 2
            assert any(p["name"] == "extended_analysis_extractor" for p in plugins)
    
    def test_error_handling_integration(self, temp_resume_file):
        """Test error handling across the system."""
        with patch('cvinsight.client.LLMService') as mock_llm, \
             patch('cvinsight.client.PluginManager') as mock_pm, \
             patch('cvinsight.client.ResumeProcessor') as mock_rp:
            
            # Setup mock to raise an exception
            mock_processor = Mock()
            mock_processor.process_resume.side_effect = Exception("Test error")
            mock_rp.return_value = mock_processor
            
            client = CVInsightClient(api_key="test-key")
            
            # Should handle errors gracefully
            with pytest.raises(Exception):
                client.extract_all(temp_resume_file)
    
    def test_api_integration(self, temp_resume_file):
        """Test API module integration."""
        from cvinsight import api
        
        with patch('cvinsight.api._get_processor') as mock_get_processor:
            mock_processor = Mock()
            mock_resume = Mock()
            mock_resume.model_dump.return_value = {
                "name": "John Doe",
                "skills": ["Python", "JavaScript"]
            }
            # Make token_usage JSON serializable
            mock_resume.token_usage = {
                "total_tokens": 150,
                "input_tokens": 100,
                "output_tokens": 50
            }
            mock_processor.process_resume.return_value = mock_resume
            mock_get_processor.return_value = mock_processor
            
            # Configure API
            api.configure("test-api-key")
            
            # Test extraction
            result = api.extract_all(temp_resume_file)
            
            assert isinstance(result, dict)
            assert "name" in result
            assert "skills" in result
    
    def test_token_usage_logging(self, temp_resume_file):
        """Test token usage logging functionality."""
        with patch('cvinsight.client.LLMService') as mock_llm, \
             patch('cvinsight.client.PluginManager') as mock_pm, \
             patch('cvinsight.client.ResumeProcessor') as mock_rp, \
             tempfile.TemporaryDirectory() as temp_dir:
            
            # Setup mock
            mock_resume = Mock()
            mock_resume.model_dump.return_value = {"name": "John Doe"}
            mock_resume.token_usage = {
                "total_tokens": 1500,
                "input_tokens": 1000,
                "output_tokens": 500
            }
            mock_resume.file_name = "test_resume.txt"
            
            mock_processor = Mock()
            mock_processor.process_resume.return_value = mock_resume
            mock_rp.return_value = mock_processor
            
            # Change to temp directory for log files
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                client = CVInsightClient(api_key="test-key")
                result = client.extract_all(temp_resume_file, log_token_usage=True)
                
                # Since we're mocking the processor, just check that the function completes
                # without error and logs directory is created by the extract_all method
                logs_dir = os.path.join(temp_dir, "logs")
                assert os.path.exists(logs_dir), "Logs directory should be created"
                
            finally:
                os.chdir(original_cwd)
