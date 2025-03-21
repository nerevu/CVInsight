import PyPDF2
from datetime import datetime
import config
import os
import logging

def validate_file(file_path):
    """
    Validates a file to ensure it meets requirements.
    
    Args:
        file_path: Path to the file to validate.
        
    Returns:
        A tuple (is_valid, message) where is_valid is a boolean and message is an error message if invalid.
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    # Check file extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in config.ALLOWED_FILE_EXTENSIONS:
        return False, f"Invalid file type. Expected one of {config.ALLOWED_FILE_EXTENSIONS}, got {ext}"
    
    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB
    if file_size_mb > config.MAX_PDF_SIZE_MB:
        return False, f"File too large. Maximum size is {config.MAX_PDF_SIZE_MB}MB, got {file_size_mb:.2f}MB"
    
    # Try opening the PDF to verify it's valid
    try:
        with open(file_path, 'rb') as file:
            PyPDF2.PdfReader(file)
    except Exception as e:
        return False, f"Invalid PDF file: {str(e)}"
    
    return True, "File is valid"

def read_file(file_path):
    """
    Reads a PDF file and extracts the text.
    
    Args:
        file_path: The path to the PDF file.
        
    Returns:
        The extracted text.
    """
    is_valid, message = validate_file(file_path)
    if not is_valid:
        raise ValueError(message)
        
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text
    except Exception as e:
        raise IOError(f"Error reading PDF file: {e}")

def parse_date(date_str, default_day="01", default_month="01"):
    """
    Parse a date string into a datetime object.
    
    Args:
        date_str: The date string to parse.
        default_day: The default day to use if not provided.
        default_month: The default month to use if not provided.
        
    Returns:
        A datetime object.
    """
    if not date_str:
        return None
        
    try:
        return datetime.strptime(date_str, config.DATE_FORMAT)
    except ValueError:
        # Attempt to handle various date formats
        pass
    
    return None

def calculate_experience(oldest_date_str, newest_date_str):
    """
    Calculate total years of experience between oldest_working_date and newest_working_date.
    
    Args:
        oldest_date_str: The oldest working date string in "dd/mm/yyyy" format.
        newest_date_str: The newest working date string in "dd/mm/yyyy" format.
        
    Returns:
        A string representing the total experience in "X Years Y Months" format.
    """
    if not oldest_date_str or not newest_date_str:
        return "0 Years 0 Months"
    
    try:
        oldest_date = datetime.strptime(oldest_date_str, config.DATE_FORMAT)
        newest_date = datetime.strptime(newest_date_str, config.DATE_FORMAT)
    except ValueError:
        # If the date format is invalid, return default experience.
        return "0 Years 0 Months"
    
    # Calculate total months of difference.
    total_months = (newest_date.year - oldest_date.year) * 12 + (newest_date.month - oldest_date.month)
    
    # Adjust if the day of the month in the newest date is less than the oldest date.
    if newest_date.day < oldest_date.day:
        total_months -= 1
    
    years = total_months // 12
    months = total_months % 12
    
    return f"{years} Years {months} Months" 