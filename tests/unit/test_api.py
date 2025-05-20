"""Unit tests for CVInsight API functions."""
import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from cvinsight.api import (
    extract_all,
    extract_profile,
    extract_skills,
    extract_education,
    extract_experience,
    extract_years_of_experience,
    analyze_resume,
    list_all_plugins,
    list_plugins_by_category
)

def test_extract_all(mock_processor, sample_resume_path, sample_resume_data):
    """Test extract_all function."""
    # Mock the processor's process_resume method
    mock_processor.process_resume.return_value = MagicMock(
        model_dump=lambda exclude: sample_resume_data
    )
    mock_processor.plugin_manager = MagicMock()
    
    with patch('cvinsight.api._get_processor', return_value=mock_processor):
        result = extract_all(sample_resume_path)
        
        assert result == sample_resume_data
        mock_processor.process_resume.assert_called_once_with(str(sample_resume_path))

def test_extract_profile(mock_plugin_manager, sample_resume_path, sample_resume_text):
    """Test extract_profile function."""
    # Mock the plugin manager and plugin
    mock_plugin = MagicMock()
    mock_plugin.extract.return_value = ({"name": "John Doe", "email": "john@example.com"}, None)
    mock_plugin_manager.get_plugin.return_value = mock_plugin
    
    with patch('cvinsight.api._get_plugin_manager', return_value=mock_plugin_manager), \
         patch('cvinsight.core.utils.file_utils.read_file', return_value=sample_resume_text):
        result = extract_profile(sample_resume_path)
        
        assert result == {"name": "John Doe", "email": "john@example.com"}
        mock_plugin_manager.get_plugin.assert_called_once_with("profile_extractor")
        mock_plugin.extract.assert_called_once_with(sample_resume_text)

def test_extract_skills(mock_plugin_manager, sample_resume_path, sample_resume_text):
    """Test extract_skills function."""
    # Mock the plugin manager and plugin
    mock_plugin = MagicMock()
    mock_plugin.extract.return_value = ({"skills": ["Python", "JavaScript"]}, None)
    mock_plugin_manager.get_plugin.return_value = mock_plugin
    
    with patch('cvinsight.api._get_plugin_manager', return_value=mock_plugin_manager), \
         patch('cvinsight.core.utils.file_utils.read_file', return_value=sample_resume_text):
        result = extract_skills(sample_resume_path)
        
        assert result == ["Python", "JavaScript"]
        mock_plugin_manager.get_plugin.assert_called_once_with("skills_extractor")
        mock_plugin.extract.assert_called_once_with(sample_resume_text)

def test_extract_education(mock_plugin_manager, sample_resume_path, sample_resume_text):
    """Test extract_education function."""
    # Mock the plugin manager and plugin
    mock_plugin = MagicMock()
    mock_plugin.extract.return_value = ({"educations": [{"degree": "BS", "institution": "University"}]}, None)
    mock_plugin_manager.get_plugin.return_value = mock_plugin
    
    with patch('cvinsight.api._get_plugin_manager', return_value=mock_plugin_manager), \
         patch('cvinsight.core.utils.file_utils.read_file', return_value=sample_resume_text):
        result = extract_education(sample_resume_path)
        
        assert result == [{"degree": "BS", "institution": "University"}]
        mock_plugin_manager.get_plugin.assert_called_once_with("education_extractor")
        mock_plugin.extract.assert_called_once_with(sample_resume_text)

def test_extract_experience(mock_plugin_manager, sample_resume_path, sample_resume_text):
    """Test extract_experience function."""
    # Mock the plugin manager and plugin
    mock_plugin = MagicMock()
    mock_plugin.extract.return_value = ({"work_experiences": [{"company": "Tech Corp", "role": "Engineer"}]}, None)
    mock_plugin_manager.get_plugin.return_value = mock_plugin
    
    with patch('cvinsight.api._get_plugin_manager', return_value=mock_plugin_manager), \
         patch('cvinsight.core.utils.file_utils.read_file', return_value=sample_resume_text):
        result = extract_experience(sample_resume_path)
        
        assert result == [{"company": "Tech Corp", "role": "Engineer"}]
        mock_plugin_manager.get_plugin.assert_called_once_with("experience_extractor")
        mock_plugin.extract.assert_called_once_with(sample_resume_text)

def test_extract_years_of_experience(mock_plugin_manager, sample_resume_path):
    """Test extract_years_of_experience function."""
    # Mock the plugin manager and plugin
    mock_plugin = MagicMock()
    mock_plugin.extract.return_value = ({"YoE": "5+ years"}, None)
    mock_plugin_manager.get_plugin.return_value = mock_plugin
    
    with patch('cvinsight.api._get_plugin_manager', return_value=mock_plugin_manager), \
         patch('cvinsight.api.extract_experience', return_value=[{"company": "Tech Corp"}]):
        result = extract_years_of_experience(sample_resume_path)
        
        assert result == "5+ years"
        mock_plugin_manager.get_plugin.assert_called_once_with("yoe_extractor")
        mock_plugin.extract.assert_called_once_with([{"company": "Tech Corp"}])

def test_analyze_resume(mock_processor, sample_resume_path, sample_resume_data):
    """Test analyze_resume function."""
    # Mock the processor's process_resume method
    mock_processor.process_resume.return_value = MagicMock(
        model_dump=lambda exclude: sample_resume_data
    )
    mock_processor.plugin_manager = MagicMock()
    mock_processor.plugin_manager.plugins = {}
    
    with patch('cvinsight.api._get_processor', return_value=mock_processor):
        result = analyze_resume(sample_resume_path, plugins=["profile_extractor"])
        
        assert result == sample_resume_data
        mock_processor.process_resume.assert_called_once_with(str(sample_resume_path))

def test_list_all_plugins(mock_plugin_manager):
    """Test list_all_plugins function."""
    # Mock the plugin manager's get_plugin_info method
    mock_plugin_manager.get_plugin_info.return_value = [
        {"name": "plugin1", "version": "1.0", "description": "Test plugin"}
    ]
    
    with patch('cvinsight.api._get_plugin_manager', return_value=mock_plugin_manager):
        result = list_all_plugins()
        
        assert result == [{"name": "plugin1", "version": "1.0", "description": "Test plugin"}]
        mock_plugin_manager.get_plugin_info.assert_called_once()

def test_list_plugins_by_category(mock_plugin_manager):
    """Test list_plugins_by_category function."""
    # Mock the plugin manager's get_plugins_by_category method
    mock_plugin = MagicMock()
    mock_plugin.metadata.name = "plugin1"
    mock_plugin.metadata.version = "1.0"
    mock_plugin.metadata.description = "Test plugin"
    mock_plugin.metadata.category.name = "extractor"
    mock_plugin.metadata.author = "Test Author"
    
    mock_plugin_manager.get_plugins_by_category.return_value = [mock_plugin]
    
    with patch('cvinsight.api._get_plugin_manager', return_value=mock_plugin_manager):
        result = list_plugins_by_category("extractor")
        
        assert result == [{
            "name": "plugin1",
            "version": "1.0",
            "description": "Test plugin",
            "category": "extractor",
            "author": "Test Author"
        }]
        mock_plugin_manager.get_plugins_by_category.assert_called_once_with("extractor") 