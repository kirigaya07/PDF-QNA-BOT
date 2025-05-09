"""
Pydantic Schemas for PDF Q&A Application
----------------------------------------
This module defines Pydantic models for request and response validation,
data serialization, and API documentation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Document schemas
class DocumentBase(BaseModel):
    """Base schema with common document attributes."""
    filename: str = Field(..., description="Filename with timestamp as stored on disk")
    original_filename: str = Field(..., description="Original filename provided during upload")
    upload_date: datetime = Field(..., description="When the document was uploaded")
    file_path: str = Field(..., description="Path to the stored file")
    text_content: str = Field(..., description="Extracted text content from the PDF")

class DocumentOut(DocumentBase):
    """Schema for document responses returned by the API."""
    id: int = Field(..., description="Unique identifier for the document")

    class Config:
        from_attributes = True  # Use 'from_attributes' instead of 'orm_mode'
        schema_extra = {
            "example": {
                "id": 1,
                "filename": "20230615_123045_sample.pdf",
                "original_filename": "sample.pdf",
                "upload_date": "2023-06-15T12:30:45",
                "file_path": "uploads/20230615_123045_sample.pdf",
                "text_content": "Sample text content from the PDF document..."
            }
        }

# API request and response schemas
class Question(BaseModel):
    """Schema for question requests."""
    document_id: int = Field(..., description="ID of the document to query")
    question: str = Field(..., description="Question to ask about the document")

class Answer(BaseModel):
    """Schema for answers returned by the Q&A engine."""
    answer: str = Field(..., description="Answer to the question")

class DocumentCreateResponse(BaseModel):
    """Response schema for document creation endpoint."""
    message: str = Field(..., description="Success message")
    document_id: int = Field(..., description="ID of the created document")

class DocumentDeleteResponse(BaseModel):
    """Response schema for document deletion endpoint."""
    message: str = Field(..., description="Success message")
    id: int = Field(..., description="ID of the deleted document")

class SuggestedQuestions(BaseModel):
    """Schema for suggested questions based on document content."""
    questions: List[str] = Field(..., description="List of suggested questions")
