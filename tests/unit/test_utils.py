"""Unit tests for utility functions in the core/utils/ directory."""
import pytest
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime, timedelta
import shutil

# Date utils
from cvinsight.core.utils.date_utils import parse_date, calculate_experience

# File utils
from cvinsight.core.utils.file_utils import validate_file, read_file, read_pdf_file, read_docx_file

# Cleanup utils
from cvinsight.core.utils.cleanup import cleanup_pycache

# Logging utils
from cvinsight.core.utils.logging_utils import setup_logging
from cvinsight.core.utils.log_utils import cleanup_token_usage_logs

class TestDateUtils:
    """Tests for date utility functions"""
    
    @patch('cvinsight.core.config.DATE_FORMAT', "%d/%m/%Y")
    def test_parse_date(self):
        """Test parsing dates with various formats"""
        # Test with a valid date directly - can't patch strptime as it's a builtin
        result = parse_date("01/01/2020")
        assert result is not None
        
        # Mock a ValueError to simulate invalid date
        with patch('cvinsight.core.utils.date_utils.datetime') as mock_dt:
            # Mock strptime to raise ValueError
            mock_dt.strptime.side_effect = ValueError("Invalid date")
            
            # Test with invalid date
            result = parse_date("invalid date")
            assert result is None
        
        # Test with empty string
        result = parse_date("")
        assert result is None
        
        # Test with None
        result = parse_date(None)
        assert result is None
    
    @patch('cvinsight.core.config.DATE_FORMAT', "%d/%m/%Y")
    def test_calculate_experience(self):
        """Test calculating years of experience between dates"""
        # Test with valid dates
        result = calculate_experience("01/01/2015", "01/01/2020")
        assert result == "5 Years 0 Months"
        
        # Test with different months
        result = calculate_experience("01/01/2015", "01/06/2020")
        assert result == "5 Years 5 Months"
        
        # Test with day adjustment
        result = calculate_experience("15/01/2015", "10/01/2020")
        assert result == "4 Years 11 Months"
        
        # Test with empty strings
        result = calculate_experience("", "")
        assert result == "0 Years 0 Months"
        
        # Test with invalid date format
        result = calculate_experience("invalid", "01/01/2020")
        assert result == "0 Years 0 Months"

class TestFileUtils:
    """Tests for file utility functions"""
    
    def test_validate_file(self):
        """Test file validation with various file types"""
        # Create a temp PDF file for testing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"%PDF-1.5\n%Test PDF content")
            temp_file.flush()
            
            # Test PDF file validation with mocked PdfReader
            with patch('PyPDF2.PdfReader') as mock_pdf_reader:
                is_valid, _ = validate_file(temp_file.name)
                assert is_valid is True
                mock_pdf_reader.assert_called_once()
            
            # Clean up
            temp_file.close()
            os.unlink(temp_file.name)
        
        # Test file that doesn't exist
        is_valid, message = validate_file("non_existent_file.pdf")
        assert is_valid is False
        assert "not found" in message
        
        # Test file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"Test text content")
            temp_file.flush()
            
            is_valid, message = validate_file(temp_file.name)
            assert is_valid is False
            assert "Invalid file type" in message
            
            # Clean up
            temp_file.close()
            os.unlink(temp_file.name)
        
        # Test file size limit
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"%PDF-1.5\n%Test PDF content")
            temp_file.flush()
            
            # Mock large file size
            with patch('os.path.getsize', return_value=30 * 1024 * 1024):  # 30MB
                is_valid, message = validate_file(temp_file.name)
                assert is_valid is False
                assert "File too large" in message
            
            # Clean up
            temp_file.close()
            os.unlink(temp_file.name)
    
    def test_read_file(self):
        """Test reading different file types"""
        # Mock validate_file to avoid PDF validation errors
        with patch('cvinsight.core.utils.file_utils.validate_file', return_value=(True, "")):
            # Mock read_pdf_file for PDF files
            with patch('cvinsight.core.utils.file_utils.read_pdf_file', return_value="PDF content"):
                # Create temp PDF file
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                    temp_file.write(b"%PDF-1.5\n%Test PDF content")
                    temp_file.flush()
                    
                    content = read_file(temp_file.name)
                    assert content == "PDF content"
                    
                    # Clean up
                    temp_file.close()
                    os.unlink(temp_file.name)
            
            # Test with unsupported file extension
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
                temp_file.write(b"Test text content")
                temp_file.flush()
                
                # Override the validation for this test
                with patch('os.path.splitext', return_value=("test", ".txt")):
                    with pytest.raises(ValueError, match="Unsupported file type"):
                        read_file(temp_file.name)
                
                # Clean up
                temp_file.close()
                os.unlink(temp_file.name)
    
    def test_read_pdf_file(self):
        """Test reading PDF files"""
        # Create a mock PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"%PDF-1.5\n%Test PDF content")
            temp_file.flush()
            
            # Mock PyPDF2.PdfReader and page extraction
            with patch('PyPDF2.PdfReader') as mock_reader:
                mock_page1 = MagicMock()
                mock_page1.extract_text.return_value = "Page 1 content"
                mock_page2 = MagicMock()
                mock_page2.extract_text.return_value = "Page 2 content"
                
                # Set up the mock reader
                mock_reader_instance = MagicMock()
                mock_reader_instance.pages = [mock_page1, mock_page2]
                mock_reader.return_value = mock_reader_instance
                
                # Read the PDF
                content = read_pdf_file(temp_file.name)
                
                # Verify content
                assert "Page 1 content" in content
                assert "Page 2 content" in content
            
            # Clean up
            temp_file.close()
            os.unlink(temp_file.name)
        
        # Test handling of exceptions
        with pytest.raises(IOError):
            read_pdf_file("non_existent.pdf")
    
    def test_read_docx_file(self):
        """Test reading DOCX files"""
        # Create a mock DOCX file
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
            temp_file.write(b"Mock DOCX content")
            temp_file.flush()
            
            # Mock docx2txt.process
            with patch('docx2txt.process', return_value="Extracted DOCX content"):
                # Read the DOCX
                content = read_docx_file(temp_file.name)
                
                # Verify content
                assert content == "Extracted DOCX content"
            
            # Clean up
            temp_file.close()
            os.unlink(temp_file.name)
        
        # Test handling of exceptions
        with patch('docx2txt.process', side_effect=Exception("Test error")):
            with pytest.raises(IOError):
                read_docx_file("test.docx")

class TestCleanupUtils:
    """Tests for cleanup utility functions"""
    
    def test_cleanup_pycache(self):
        """Test cleaning up __pycache__ directories"""
        # Create a temporary directory structure with __pycache__ folders
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create __pycache__ directories
            pycache_dir1 = os.path.join(temp_dir, "__pycache__")
            pycache_dir2 = os.path.join(temp_dir, "subdir", "__pycache__")
            
            # Create directory structure
            os.makedirs(pycache_dir1, exist_ok=True)
            os.makedirs(pycache_dir2, exist_ok=True)
            
            # Create some test files
            with open(os.path.join(pycache_dir1, "test.pyc"), "w") as f:
                f.write("Test pyc file")
            
            # Run cleanup
            cleanup_pycache(temp_dir)
            
            # Check that __pycache__ directories are removed
            assert not os.path.exists(pycache_dir1)
            assert not os.path.exists(pycache_dir2)

class TestLoggingUtils:
    """Tests for logging utility functions"""
    
    def test_setup_logging(self):
        """Test setting up logging configurations"""
        with patch('logging.basicConfig') as mock_basic_config, \
             patch('logging.info') as mock_info, \
             patch('os.path.exists', return_value=False), \
             patch('os.makedirs') as mock_makedirs, \
             patch('logging.handlers.RotatingFileHandler') as mock_handler:
            
            # Call setup_logging
            logger = setup_logging()
            
            # Verify that logging was configured
            mock_basic_config.assert_called_once()
            mock_info.assert_called_with("Resume Analysis application started")
    
    def test_cleanup_token_usage_logs(self):
        """Test cleaning up token usage logs"""
        # Create a temporary log directory
        with tempfile.TemporaryDirectory() as log_dir:
            # Create test log files with proper timestamp format
            # Old files (from 2020) will be removed
            old_log1 = os.path.join(log_dir, "resume1_token_usage_20200101_000000.json")
            old_log2 = os.path.join(log_dir, "resume2_token_usage_20200101_000000.json")
            old_log3 = os.path.join(log_dir, "resume3_token_usage_20200101_000000.json")
            
            # Recent file (from today) should not be removed
            today = datetime.now().strftime("%Y%m%d_%H%M%S")
            recent_log = os.path.join(log_dir, f"resume_token_usage_{today}.json")
            
            # Create log files
            with open(old_log1, "w") as f:
                f.write('{"tokens": 100}')
            with open(old_log2, "w") as f:
                f.write('{"tokens": 150}')
            with open(old_log3, "w") as f:
                f.write('{"tokens": 200}')
            with open(recent_log, "w") as f:
                f.write('{"tokens": 200}')
            
            # Create a non-token-usage log file to ensure it's not affected
            other_log = os.path.join(log_dir, "other_log.json")
            with open(other_log, "w") as f:
                f.write('{"data": "test"}')
            
            # Run cleanup with patched datetime and config 
            with patch('datetime.datetime') as mock_datetime, \
                 patch('cvinsight.core.config.TOKEN_LOG_RETENTION_DAYS', 7):
                
                # Mock current time to be fixed at 2023-01-15
                mock_now = MagicMock()
                mock_now.year = 2023
                mock_now.month = 1
                mock_now.day = 15
                
                # Set up cutoff date to be 2023-01-08 (7 days before mock_now)
                mock_cutoff = MagicMock()
                mock_cutoff.year = 2023
                mock_cutoff.month = 1
                mock_cutoff.day = 8
                
                # Mock the now() method to return our fixed date
                mock_datetime.now.return_value = mock_now
                
                # Mock datetime subtraction to return our cutoff date
                mock_now.__sub__.return_value = mock_cutoff
                
                # Mock the datetime parsing to handle our test dates
                def mock_strptime(date_str, format_str):
                    if "20200101" in date_str:
                        # Return a date from 2020 (old, should be removed)
                        result = MagicMock()
                        result.year = 2020
                        result.month = 1
                        result.day = 1
                        result.__lt__.return_value = True  # Will be < cutoff
                        return result
                    else:
                        # Return today's date (recent, should be kept)
                        result = MagicMock()
                        result.year = 2023
                        result.month = 1
                        result.day = 14  # Just one day before mock_now
                        result.__lt__.return_value = False  # Will not be < cutoff
                        return result
                    
                mock_datetime.strptime.side_effect = mock_strptime
                
                # Run cleanup
                count, removed = cleanup_token_usage_logs(log_dir)
                
                # Check that files were processed correctly
                assert "resume1_token_usage_20200101_000000.json" in removed
                assert "resume2_token_usage_20200101_000000.json" in removed
                assert "resume3_token_usage_20200101_000000.json" in removed
                
                # Recent files should still exist, old files should be gone
                assert not os.path.exists(old_log1)
                assert not os.path.exists(old_log2)
                assert not os.path.exists(old_log3)
                assert os.path.exists(recent_log)
                assert os.path.exists(other_log) 