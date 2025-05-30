"""Test notebook utility functions."""
import pytest
import os
import sys
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add the parent directory to the path so we can import cvinsight
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from cvinsight.notebook_utils import (
    initialize_client, 
    parse_single_resume, 
    parse_many_resumes, 
    find_resumes
)
import os


class TestNotebookUtils:
    """Test the notebook utility functions."""
    
    @pytest.fixture
    def mock_api_key(self):
        return "test-api-key-12345"
    
    def test_initialize_client(self, mock_api_key):
        """Test client initialization."""
        with patch('cvinsight.notebook_utils.CVInsightClient') as mock_client_class, \
             patch('cvinsight.notebook_utils.ExtendedAnalysisExtractorPlugin') as mock_plugin:
            
            mock_client = Mock()
            mock_client._llm_service = Mock()
            mock_client._plugin_manager = Mock()
            mock_client._plugin_manager.plugins = {}
            mock_client._plugin_manager.extractors = {}
            mock_client_class.return_value = mock_client
            
            result = initialize_client(mock_api_key, provider="openai")
            
            # Check that client was created with correct parameters
            mock_client_class.assert_called_once_with(
                api_key=mock_api_key,
                provider="openai",
                model_name="o4-mini-2025-04-16"
            )
            
            # Check that plugin was registered
            assert "extended_analysis_extractor" in mock_client._plugin_manager.plugins
            assert "extended_analysis_extractor" in mock_client._plugin_manager.extractors
            
            assert result == mock_client
    
    def test_parse_single_resume(self):
        """Test parsing a single resume."""
        mock_client = Mock()
        mock_result = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "Machine Learning"],
            "plugin_data": {},
            "parsing_status": "success"
        }
        
        with patch('cvinsight.core.utils.file_utils.read_file', return_value="Fake resume text"), \
             patch('cvinsight.notebook_utils.extract_with_optimized_plugins', return_value=mock_result):
            
            result = parse_single_resume(
                client=mock_client,
                resume_path="fake_resume.pdf",
                date_of_resume_submission="2024-01-01",
                job_description="Software Engineer position"
            )
            
            assert isinstance(result, dict)
            assert result["filename"] == "fake_resume.pdf"
            assert result["parsing_status"] == "success"
            assert result["name"] == "John Doe"
            assert result["email"] == "john@example.com"
    
    def test_parse_single_resume_with_error(self):
        """Test parsing a single resume with error handling."""
        mock_client = Mock()
        
        with patch('cvinsight.core.utils.file_utils.read_file', return_value="Fake resume text"), \
             patch('cvinsight.notebook_utils.extract_with_optimized_plugins', side_effect=Exception("Test error")):
            
            result = parse_single_resume(
                client=mock_client,
                resume_path="fake_resume.pdf"
            )
            
            assert isinstance(result, dict)
            assert result["parsing_status"] == "failed"
            assert "error" in result
            assert result["filename"] == "fake_resume.pdf"
    
    def test_parse_many_resumes_sequential(self):
        """Test parsing multiple resumes sequentially."""
        mock_client = Mock()
        
        # Mock successful parsing
        def mock_extract_all(path):
            return {
                "name": f"Person {path}",
                "email": f"person{path}@example.com",
                "skills": ["Python"],
                "parsing_status": "success"
            }
        
        mock_client.extract_all.side_effect = mock_extract_all
        
        resume_paths = ["resume1.pdf", "resume2.pdf"]
        
        with patch('cvinsight.notebook_utils.parse_single_resume') as mock_parse:
            mock_parse.side_effect = [
                {"name": "Person 1", "parsing_status": "success", "filename": "resume1.pdf"},
                {"name": "Person 2", "parsing_status": "success", "filename": "resume2.pdf"}
            ]
            
            result = parse_many_resumes(
                client=mock_client,
                resume_paths=resume_paths,
                parallel=False
            )
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert mock_parse.call_count == 2
    
    def test_parse_many_resumes_parallel(self):
        """Test parsing multiple resumes in parallel."""
        mock_client = Mock()
        resume_paths = ["resume1.pdf", "resume2.pdf"]
        
        # Mock the parse_single_resume function to return instantly
        def mock_parse_function(*args, **kwargs):
            return {"name": f"Person {len(args)}", "parsing_status": "success"}
        
        with patch('cvinsight.notebook_utils.parse_single_resume', side_effect=mock_parse_function):
            result = parse_many_resumes(
                client=mock_client,
                resume_paths=resume_paths,
                parallel=True,
                max_workers=2
            )
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert all(result['parsing_status'] == 'success')
    
    def test_find_resumes(self):
        """Test finding resume files in a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            pdf_file = os.path.join(temp_dir, "resume1.pdf")
            docx_file = os.path.join(temp_dir, "resume2.docx")
            txt_file = os.path.join(temp_dir, "resume3.txt")
            other_file = os.path.join(temp_dir, "other.xyz")
            
            for file_path in [pdf_file, docx_file, txt_file, other_file]:
                with open(file_path, 'w') as f:
                    f.write("test content")
            
            result = find_resumes(temp_dir)
            
            assert isinstance(result, list)
            assert len(result) == 2  # Only PDF and DOCX files (TXT is not supported)
            
            # Check that all returned files exist and have correct extensions
            for file_path in result:
                assert os.path.exists(file_path)
                assert any(file_path.endswith(ext) for ext in ['.pdf', '.docx'])
    
    def test_find_resumes_empty_directory(self):
        """Test finding resumes in an empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = find_resumes(temp_dir)
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_find_resumes_nonexistent_directory(self):
        """Test finding resumes in a non-existent directory."""
        result = find_resumes("/nonexistent/directory")
        
        assert isinstance(result, list)
        assert len(result) == 0
