"""Test the unified ExtendedAnalysisExtractorPlugin."""
import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path so we can import cvinsight
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from cvinsight.custom_plugins.extended_analysis_extractor.extended_analysis_extractor import (
    ExtendedAnalysisExtractorPlugin,
    ExtendedAnalysisData,
    DegreeStatus,
    SchoolPrestige,
    SeniorityLevel
)


class TestExtendedAnalysisExtractorPlugin:
    """Test the unified ExtendedAnalysisExtractorPlugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create a plugin instance for testing."""
        mock_llm_service = Mock()
        return ExtendedAnalysisExtractorPlugin(
            job_description="Software Engineer position requiring Python and ML skills",
            date_of_resume_submission="2024-01-01",
            llm_service=mock_llm_service
        )
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        mock_llm_service = Mock()
        plugin = ExtendedAnalysisExtractorPlugin(llm_service=mock_llm_service)
        
        assert plugin.llm_service == mock_llm_service
        assert plugin.job_description is not None  # Should have default
        assert plugin.date_of_resume_submission is None
    
    def test_plugin_metadata(self, plugin):
        """Test plugin metadata."""
        metadata = plugin.metadata
        
        assert metadata.name == "extended_analysis_extractor"
        assert metadata.version == "1.0.0"
        assert "unified extractor" in metadata.description.lower()
        assert metadata.author == "AI Assistant"
    
    def test_get_model(self, plugin):
        """Test get_model method."""
        model = plugin.get_model()
        assert model == ExtendedAnalysisData
    
    def test_get_input_variables(self, plugin):
        """Test get_input_variables method."""
        variables = plugin.get_input_variables()
        expected_vars = ["text", "job_description", "submission_date", "seniority_levels"]
        
        assert isinstance(variables, list)
        assert all(var in variables for var in expected_vars)
    
    def test_prepare_input_data(self, plugin):
        """Test prepare_input_data method."""
        test_text = "Sample resume text"
        input_data = plugin.prepare_input_data(test_text)
        
        assert isinstance(input_data, dict)
        assert input_data["text"] == test_text
        assert input_data["job_description"] == plugin.job_description
        assert "submission_date" in input_data
        assert "seniority_levels" in input_data
    
    def test_map_degree_to_years(self, plugin):
        """Test degree mapping logic."""
        # Test PhD
        phd_info = {"highest_degree": "PhD in Computer Science", "highest_degree_status": "completed"}
        assert plugin.map_degree_to_years(phd_info) == 8.0
        
        # Test pursuing PhD
        phd_pursuing = {"highest_degree": "PhD in Computer Science", "highest_degree_status": "pursuing"}
        assert plugin.map_degree_to_years(phd_pursuing) == 7.0
        
        # Test Master's
        masters_info = {"highest_degree": "Master of Science", "highest_degree_status": "completed"}
        assert plugin.map_degree_to_years(masters_info) == 6.0
        
        # Test pursuing Master's
        masters_pursuing = {"highest_degree": "Master of Science", "highest_degree_status": "pursuing"}
        assert plugin.map_degree_to_years(masters_pursuing) == 3.0
        
        # Test Bachelor's
        bachelors_info = {"highest_degree": "Bachelor of Science", "highest_degree_status": "completed"}
        assert plugin.map_degree_to_years(bachelors_info) == 4.0
        
        # Test Associate's
        associate_info = {"highest_degree": "Associate Degree", "highest_degree_status": "completed"}
        assert plugin.map_degree_to_years(associate_info) == 2.0
        
        # Test no degree
        no_degree = {"highest_degree": "", "highest_degree_status": "unknown"}
        assert plugin.map_degree_to_years(no_degree) == 0.0
    
    def test_process_output(self, plugin):
        """Test process_output method."""
        # Mock LLM result
        llm_result = {
            "all_wyoe": 5.0,
            "all_relevant_wyoe": 3.0,
            "all_eyoe": 4.0,
            "relevant_eyoe": 4.0,
            "highest_degree": "Master of Science in Computer Science",
            "highest_degree_status": "completed",
            "highest_degree_major": "Computer Science",
            "highest_seniority_level": "senior",
            "primary_position_title": "Software Engineer"
        }
        
        result = plugin.process_output(llm_result)
        
        assert isinstance(result, dict)
        # Should map education years based on degree
        assert result["all_eyoe"] == 6.0  # Master's should be 6 years
        assert "all_wyoe" in result
        assert "all_relevant_wyoe" in result
    
    def test_extract_method(self, plugin):
        """Test the main extract method."""
        # Mock LLM service response
        mock_llm_result = {
            "all_wyoe": 5.0,
            "all_relevant_wyoe": 3.0,
            "all_eyoe": 4.0,
            "relevant_eyoe": 4.0,
            "highest_degree": "Bachelor of Science",
            "highest_degree_status": "completed",
            "highest_seniority_level": "mid-level",
            "phone_number": "2135551234",
            "email": "test@example.com"
        }
        
        mock_token_usage = {
            "input_tokens": 1000,
            "output_tokens": 200,
            "total_tokens": 1200
        }
        
        plugin.llm_service.extract_with_llm.return_value = (mock_llm_result, mock_token_usage)
        
        test_text = "Sample resume text with experience and education information."
        
        result, token_usage = plugin.extract(test_text)
        
        assert isinstance(result, dict)
        assert isinstance(token_usage, dict)
        
        # Check that LLM was called
        plugin.llm_service.extract_with_llm.assert_called_once()
        
        # Check that result contains expected fields
        assert "all_wyoe" in result
        assert "all_relevant_wyoe" in result
        assert "all_eyoe" in result
        assert "highest_degree" in result
        
        # Check token usage
        assert token_usage["extractor"] == "extended_analysis_extractor"
    
    def test_extract_with_additional_params(self, plugin):
        """Test extract method with additional parameters."""
        mock_llm_result = {
            "all_wyoe": 3.0,
            "all_relevant_wyoe": 2.0,
            "highest_degree": "Master of Arts",
            "highest_degree_status": "completed"
        }
        
        mock_token_usage = {"total_tokens": 800}
        plugin.llm_service.extract_with_llm.return_value = (mock_llm_result, mock_token_usage)
        
        additional_params = {
            "job_description": "Data Analyst position",
            "date_of_resume_submission": "2024-02-01"
        }
        
        result, token_usage = plugin.extract("Sample text", additional_params)
        
        assert isinstance(result, dict)
        # Original values should be restored after extraction
        assert plugin.job_description != "Data Analyst position"  # Should be restored
    
    def test_phone_number_formatting(self):
        """Test phone number formatting validator."""
        # Test US number formatting
        data = ExtendedAnalysisData(phone_number="2135551234")
        assert data.phone_number == "1-213-555-1234"
        
        # Test 11-digit number
        data = ExtendedAnalysisData(phone_number="12135551234")
        assert data.phone_number == "1-213-555-1234"
        
        # Test with existing formatting
        data = ExtendedAnalysisData(phone_number="213-555-1234")
        assert data.phone_number == "1-213-555-1234"
        
        # Test international number (should remain unchanged)
        data = ExtendedAnalysisData(phone_number="+44 20 7946 0958")
        assert data.phone_number == "+44 20 7946 0958"
    
    def test_enums(self):
        """Test enum values."""
        # Test DegreeStatus
        assert DegreeStatus.COMPLETED.value == "completed"
        assert DegreeStatus.PURSUING.value == "pursuing"
        assert DegreeStatus.UNKNOWN.value == "unknown"
        
        # Test SchoolPrestige
        assert SchoolPrestige.LOW.value == "low"
        assert SchoolPrestige.MEDIUM.value == "medium"
        assert SchoolPrestige.HIGH.value == "high"
        
        # Test SeniorityLevel
        assert SeniorityLevel.JUNIOR.value == "junior"
        assert SeniorityLevel.SENIOR.value == "senior"
        assert SeniorityLevel.EXECUTIVE.value == "executive"
