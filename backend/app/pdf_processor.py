"""
PDF Processing Module
--------------------
This module handles the extraction of text content from PDF files
for later use in the question answering system.
"""

from PyPDF2 import PdfReader
import os
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Handles the processing and text extraction of PDF documents.
    
    This class provides methods to extract text content from PDF files
    using PyPDF2, with robust error handling and logging.
    """
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF file using PyPDF2.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            Exception: For other PDF processing errors
        """
        logger.info(f"Extracting text from PDF: {file_path}")
        
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                logger.error(f"PDF file not found at {file_path}")
                raise FileNotFoundError(f"PDF file not found at {file_path}")
            
            # Validate file is accessible
            if not os.access(file_path, os.R_OK):
                logger.error(f"No read permission for PDF file at {file_path}")
                raise PermissionError(f"No read permission for PDF file at {file_path}")
                
            # Process the PDF
            reader = PdfReader(file_path)
            if len(reader.pages) == 0:
                logger.warning(f"PDF has no pages: {file_path}")
                return ""
            
            logger.info(f"PDF has {len(reader.pages)} pages")
            text = ""
            
            # Extract text from each page
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
                    
                    # Log progress for large PDFs
                    if i > 0 and i % 10 == 0:
                        logger.info(f"Processed {i}/{len(reader.pages)} pages")
                        
                except Exception as page_error:
                    logger.warning(f"Error extracting text from page {i+1}: {str(page_error)}")
                    # Continue with next page even if this one fails
            
            logger.info(f"Successfully extracted {len(text)} characters of text")
            return text.strip()
            
        except FileNotFoundError:
            # Re-raise specific exceptions
            raise
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise Exception(f"Error processing PDF: {str(e)}")