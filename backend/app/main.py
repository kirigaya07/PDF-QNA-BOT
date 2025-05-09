"""
PDF Q&A API - Main Application
------------------------------
This module implements a FastAPI application that allows users to:
- Upload PDF documents
- Extract and store text content in a database
- Ask questions about the documents
- Get AI-generated answers using the Gemini model
- Manage documents (list, view, delete)
- Generate suggested questions based on document content
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import os
from datetime import datetime
from typing import List, Optional

from .database import SessionLocal, engine, get_db
from . import models, schemas
from .pdf_processor import PDFProcessor
from .qa_engine import QAEngine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="PDF Q&A API",
    description="An API for uploading PDFs, extracting text, and answering questions using AI",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# API Endpoints
# --------------------------------------------------

@app.get("/")
def read_root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to the PDF Q&A API!"}

@app.get("/favicon.ico")
async def favicon():
    """Handle favicon requests to avoid 404 errors."""
    return JSONResponse(status_code=204, content={})

@app.post("/upload/", response_model=schemas.DocumentCreateResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file, extract its text, and store in the database.
    
    Args:
        file: The PDF file to upload
        
    Returns:
        A JSON response with the document ID
        
    Raises:
        HTTPException: If file validation or processing fails
    """
    logger.info(f"Received upload request for file: {file.filename}")
    
    # Validate file format
    if not file.filename.endswith('.pdf'):
        logger.warning(f"Rejected non-PDF file: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Create unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    logger.info(f"Saving file to: {file_path}")
    
    try:
        # Save file to disk in chunks to handle large files
        with file_path.open("wb") as buffer:
            while contents := await file.read(1024 * 1024):  # 1MB chunks
                buffer.write(contents)
        
        logger.info("File saved successfully")
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Process PDF and store in database
    logger.info("Extracting text from PDF...")
    db = SessionLocal()
    try:
        # Extract text from PDF
        pdf_processor = PDFProcessor()
        text_content = pdf_processor.extract_text(str(file_path))
        logger.info(f"Extracted {len(text_content)} characters of text")
        
        if not text_content:
            logger.warning("Warning: No text extracted from PDF")
        
        # Create document record
        logger.info("Creating document record in database...")
        db_document = models.Document(
            filename=filename,
            original_filename=file.filename,
            upload_date=datetime.now(),
            file_path=str(file_path),
            text_content=text_content
        )
        
        # Add to database and commit
        logger.info("Adding document to database session...")
        db.add(db_document)
        logger.info("Committing to database...")
        db.commit()
        logger.info(f"Commit successful. Document saved with ID: {db_document.id}")
        db.refresh(db_document)
        logger.info(f"Document refreshed with ID: {db_document.id}")
        
        # Verify the document was saved
        saved_doc = db.query(models.Document).filter(models.Document.id == db_document.id).first()
        if not saved_doc:
            logger.warning("WARNING: Document not found after saving!")
        else:
            logger.info(f"Document verified in database with ID: {saved_doc.id}")
            logger.info(f"Document filename: {saved_doc.filename}, length of text: {len(saved_doc.text_content) if saved_doc.text_content else 0}")
        
        logger.info("Checking total document count in database...")
        doc_count = db.query(models.Document).count()
        logger.info(f"Total document count in database: {doc_count}")
        
        return {"message": "File uploaded successfully", "document_id": db_document.id}
    except Exception as e:
        logger.error(f"Error in database operation: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
        logger.info("Database connection closed")

@app.delete("/documents/{document_id}", response_model=schemas.DocumentDeleteResponse)
async def delete_document(document_id: int):
    """
    Delete a document from the database and file system.
    
    Args:
        document_id: The ID of the document to delete
        
    Returns:
        A JSON response confirming deletion
        
    Raises:
        HTTPException: If document is not found or deletion fails
    """
    logger.info(f"Received delete request for document_id: {document_id}")
    db = SessionLocal()
    try:
        # Get document
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not document:
            logger.warning(f"Document with id {document_id} not found")
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"Found document: {document.filename}, path: {document.file_path}")
        
        # Delete the actual file
        try:
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Successfully deleted file: {document.file_path}")
            else:
                logger.warning(f"File not found: {document.file_path}")
        except Exception as file_error:
            logger.error(f"Error deleting file: {str(file_error)}")
            # Continue even if file deletion fails
        
        # Delete from database
        try:
            # ORM method
            db.delete(document)
            db.commit()
            logger.info(f"Successfully deleted document from database using ORM, id: {document_id}")
            
            # Verify deletion
            check = db.query(models.Document).filter(models.Document.id == document_id).first()
            if check:
                logger.warning(f"WARNING: Document still exists after deletion! Trying SQL method...")
                
                # Direct SQL method (fallback)
                from sqlalchemy import text
                sql = text(f"DELETE FROM documents WHERE id = :id")
                db.execute(sql, {"id": document_id})
                db.commit()
                logger.info(f"Executed direct SQL DELETE for document id: {document_id}")
        except Exception as db_error:
            logger.error(f"Error deleting from database: {str(db_error)}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        return {"message": "Document deleted successfully", "id": document_id}
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        logger.error(f"Unexpected error in delete_document: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
        logger.info("Delete operation completed, database connection closed")

@app.post("/ask/", response_model=schemas.Answer)
async def ask_question(question: schemas.Question):
    """
    Answer a question about a document using the QA engine.
    
    Args:
        question: Question object with document_id and question text
        
    Returns:
        The answer to the question
        
    Raises:
        HTTPException: If document is not found or question processing fails
    """
    logger.info(f"Received question about document {question.document_id}: {question.question}")
    db = SessionLocal()
    try:
        document = db.query(models.Document).filter(models.Document.id == question.document_id).first()
        if not document:
            logger.warning(f"Document with id {question.document_id} not found")
            raise HTTPException(status_code=404, detail="Document not found")

        logger.info(f"Found document: {document.filename}, generating answer...")
        qa_engine = QAEngine()
        answer = qa_engine.get_answer(document.text_content, question.question)
        logger.info("Answer generated successfully")

        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
        logger.info("Question answering completed, database connection closed")

@app.get("/documents/", response_model=List[schemas.DocumentOut])
async def list_documents():
    """
    List all documents in the database.
    
    Returns:
        A list of all documents
    """
    logger.info("Fetching list of all documents")
    db = SessionLocal()
    try:
        documents = db.query(models.Document).all()
        logger.info(f"Found {len(documents)} documents")
        return documents
    finally:
        db.close()
        logger.info("List documents operation completed")

@app.get("/documents/{doc_id}", response_model=schemas.DocumentOut)
async def get_document(doc_id: int):
    """
    Get a single document by ID.
    
    Args:
        doc_id: The ID of the document to retrieve
        
    Returns:
        The document details
        
    Raises:
        HTTPException: If document is not found
    """
    logger.info(f"Fetching document with ID: {doc_id}")
    db = SessionLocal()
    try:
        document = db.query(models.Document).filter(models.Document.id == doc_id).first()
        if not document:
            logger.warning(f"Document with id {doc_id} not found")
            raise HTTPException(status_code=404, detail="Document not found")
        logger.info(f"Found document: {document.filename}")
        return document
    finally:
        db.close()
        logger.info("Get document operation completed")

@app.get("/documents/{document_id}/suggested-questions", response_model=schemas.SuggestedQuestions)
async def get_suggested_questions(document_id: int):
    """
    Generate suggested questions based on the document content.
    
    Args:
        document_id: The ID of the document to generate questions for
        
    Returns:
        A list of suggested questions
        
    Raises:
        HTTPException: If document is not found or question generation fails
    """
    logger.info(f"Generating suggested questions for document ID: {document_id}")
    db = SessionLocal()
    try:
        # Get document
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not document:
            logger.warning(f"Document with id {document_id} not found")
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"Found document: {document.filename}")
        
        # Initialize QA engine
        qa_engine = QAEngine()
        
        # Generate suggested questions
        try:
            suggested_questions = qa_engine.generate_questions(document.text_content)
            logger.info(f"Generated {len(suggested_questions)} suggested questions")
            return {"questions": suggested_questions}
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")
    finally:
        db.close()
        logger.info("Suggested questions operation completed")
