"""Integration tests for CVInsight CLI."""
import os
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock
from click.testing import CliRunner
from cvinsight.cli import main

def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    
    assert result.exit_code == 0
    assert "CVInsight - AI-powered resume analysis" in result.output

def test_cli_list_plugins(mock_plugin_manager):
    """Test CLI list plugins command."""
    # Mock the plugin manager's get_plugin_info method
    mock_plugin_manager.get_plugin_info.return_value = [
        {"name": "plugin1", "version": "1.0", "description": "Test plugin"}
    ]
    
    runner = CliRunner()
    with pytest.MonkeyPatch.context() as m:
        m.setattr('cvinsight.api._get_plugin_manager', lambda: mock_plugin_manager)
        result = runner.invoke(main, ['--list-plugins'])
    
    assert result.exit_code == 0
    assert "Available plugins:" in result.output
    assert "plugin1 (v1.0): Test plugin" in result.output

def test_cli_list_plugins_json(mock_plugin_manager):
    """Test CLI list plugins command with JSON output."""
    # Mock the plugin manager's get_plugin_info method
    mock_plugin_manager.get_plugin_info.return_value = [
        {"name": "plugin1", "version": "1.0", "description": "Test plugin"}
    ]
    
    runner = CliRunner()
    with pytest.MonkeyPatch.context() as m:
        m.setattr('cvinsight.api._get_plugin_manager', lambda: mock_plugin_manager)
        result = runner.invoke(main, ['--list-plugins', '--json'])
    
    assert result.exit_code == 0
    output = json.loads(result.output)
    assert len(output) == 1
    assert output[0]["name"] == "plugin1"
    assert output[0]["version"] == "1.0"
    assert output[0]["description"] == "Test plugin"

def test_cli_process_resume(sample_resume_path, sample_resume_data, mock_processor):
    """Test CLI resume processing."""
    # Mock the processor's process_resume method
    mock_processor.process_resume.return_value = MagicMock(
        model_dump=lambda exclude: {**sample_resume_data, "years_of_experience": "5+ years"}
    )
    mock_processor.plugin_manager = MagicMock()
    
    runner = CliRunner()
    with pytest.MonkeyPatch.context() as m:
        m.setattr('cvinsight.api._get_processor', lambda: mock_processor)
        result = runner.invoke(main, ['--resume', str(sample_resume_path)])
    
    assert result.exit_code == 0
    assert "Resume Analysis Results:" in result.output
    assert "Name: John Doe" in result.output
    assert "Email: john.doe@email.com" in result.output
    assert "Skills:" in result.output
    assert "Education:" in result.output
    assert "Experience:" in result.output
    assert "Years of Experience:" in result.output

def test_cli_process_resume_json(sample_resume_path, sample_resume_data, mock_processor):
    """Test CLI resume processing with JSON output."""
    # Mock the processor's process_resume method
    mock_processor.process_resume.return_value = MagicMock(
        model_dump=lambda exclude: sample_resume_data
    )
    mock_processor.plugin_manager = MagicMock()
    
    runner = CliRunner()
    with pytest.MonkeyPatch.context() as m:
        m.setattr('cvinsight.api._get_processor', lambda: mock_processor)
        result = runner.invoke(main, ['--resume', str(sample_resume_path), '--json'])
    
    assert result.exit_code == 0
    output = json.loads(result.output)
    assert output == sample_resume_data

def test_cli_process_resume_with_plugins(sample_resume_path, sample_resume_data, mock_processor):
    """Test CLI resume processing with specific plugins."""
    # Mock the processor's process_resume method
    mock_processor.process_resume.return_value = MagicMock(
        model_dump=lambda exclude: sample_resume_data
    )
    mock_processor.plugin_manager = MagicMock()
    
    runner = CliRunner()
    with pytest.MonkeyPatch.context() as m:
        m.setattr('cvinsight.api._get_processor', lambda: mock_processor)
        result = runner.invoke(main, [
            '--resume', str(sample_resume_path),
            '--plugins', 'profile_extractor,skills_extractor'
        ])
    
    assert result.exit_code == 0
    assert "Resume Analysis Results:" in result.output

def test_cli_process_resume_with_output(sample_resume_path, sample_resume_data, mock_processor, temp_dir):
    """Test CLI resume processing with output directory."""
    # Mock the processor's process_resume method
    mock_processor.process_resume.return_value = MagicMock(
        model_dump=lambda exclude: sample_resume_data
    )
    mock_processor.plugin_manager = MagicMock()
    
    output_dir = temp_dir / "output"
    runner = CliRunner()
    with pytest.MonkeyPatch.context() as m:
        m.setattr('cvinsight.api._get_processor', lambda: mock_processor)
        result = runner.invoke(main, [
            '--resume', str(sample_resume_path),
            '--output', str(output_dir)
        ])
    
    assert result.exit_code == 0
    assert "Results saved to" in result.output
    
    # Check if the output file was created
    output_file = output_dir / "sample_resume.json"
    assert output_file.exists()
    
    # Check the contents of the output file
    with open(output_file) as f:
        saved_data = json.load(f)
    assert saved_data == sample_resume_data

def test_cli_process_resume_file_not_found():
    """Test CLI resume processing with non-existent file."""
    runner = CliRunner()
    result = runner.invoke(main, ['--resume', 'nonexistent.pdf'])
    
    assert result.exit_code == 1
    assert "Error: Resume file not found at" in result.output 