"""
Database Models for PDF Q&A Application
---------------------------------------
This module defines SQLAlchemy ORM models for storing document information
and related data in the database.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.schema import Index
from .database import Base
from datetime import datetime
from typing import Optional

class Document(Base):
    """
    Document model for storing PDF files information.
    
    This model stores metadata about uploaded PDF documents
    including the extracted text content for quick querying.
    
    Attributes:
        id: Unique identifier for the document
        filename: The filename stored on disk (with timestamp)
        original_filename: The original name of the uploaded file
        upload_date: When the document was uploaded
        file_path: Full path to the stored file
        text_content: Extracted text content from the PDF
    """
    __tablename__ = "documents"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    original_filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.now, nullable=False)
    file_path = Column(String, nullable=False)
    text_content = Column(Text)
    
    # Create an index on upload_date for efficient sorting
    __table_args__ = (
        Index('ix_documents_upload_date', 'upload_date'),
    )
    
    def __repr__(self) -> str:
        """String representation of the Document object."""
        return f"<Document(id={self.id}, filename='{self.original_filename}')>" 