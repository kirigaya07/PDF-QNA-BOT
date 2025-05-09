# PDF Q&A Application

A full-stack application that allows users to upload PDF documents, ask questions about their content, and receive AI-generated answers in a conversational interface.

## Features

- PDF upload and storage
- Text extraction from PDFs
- AI-powered question answering using Google's Gemini model
- Chat-style UI with message bubbles
- Document management (view, delete)
- Suggested questions based on document content
- PostgreSQL database integration with NeonDB

## Architecture

### Backend (FastAPI)

The backend is built with FastAPI and provides a RESTful API for the frontend. It handles:

- PDF processing and text extraction using PyPDF2
- Database operations with SQLAlchemy ORM
- Question answering with Google's Gemini AI model
- Document management

Key components:

- `main.py`: API endpoints and request handling
- `models.py`: SQLAlchemy database models
- `schemas.py`: Pydantic schemas for request/response validation
- `pdf_processor.py`: PDF text extraction logic
- `qa_engine.py`: Integration with Gemini AI for question answering
- `database.py`: Database connection and session management

### Frontend (React)

The frontend is built with React and Chakra UI and provides a user-friendly interface for:

- Uploading PDF documents
- Viewing document list
- Asking questions about documents
- Receiving AI-generated answers in a chat interface
- Suggested questions based on document content

Key components:

- `DocumentView.tsx`: Chat interface for Q&A
- `Home.tsx`: Document list and upload functionality
- `PDFUploader.tsx`: File upload with progress indication

### Database (PostgreSQL)

The application uses PostgreSQL for data storage, deployed on NeonDB cloud. It stores:

- Document metadata (filename, upload date, etc.)
- Extracted text content for fast searching

## Setup Instructions

### Prerequisites

- Python 3.8+ for backend
- Node.js and npm for frontend
- PostgreSQL database (NeonDB or local)
- Google API key for Gemini AI

### Backend Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/pdf-qa-app.git
   cd pdf-qa-app
   ```

2. Set up a virtual environment:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory:

   ```
   DATABASE_URL=postgresql://username:password@hostname:port/database
   GOOGLE_API_KEY=your_google_api_key
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm start
   ```

4. The application will be available at http://localhost:3000

## API Documentation

### Endpoints

#### Documents

- `GET /documents/` - List all documents
- `GET /documents/{id}` - Get a specific document
- `POST /upload/` - Upload a new PDF document
- `DELETE /documents/{id}` - Delete a document

#### Question Answering

- `POST /ask/` - Ask a question about a document
- `GET /documents/{id}/suggested-questions` - Get suggested questions for a document

### Request/Response Examples

#### Upload a Document

Request:

```
POST /upload/
Content-Type: multipart/form-data

file: [PDF file]
```

Response:

```json
{
  "message": "File uploaded successfully",
  "document_id": 1
}
```

#### Ask a Question

Request:

```json
POST /ask/
Content-Type: application/json

{
  "document_id": 1,
  "question": "What is the main topic of this document?"
}
```

Response:

```json
{
  "answer": "The main topic of this document is artificial intelligence and its applications in modern business."
}
```

#### Get Suggested Questions

Request:

```
GET /documents/1/suggested-questions
```

Response:

```json
{
  "questions": [
    "What are the key findings in this document?",
    "Who are the main authors referenced?",
    "What methodologies were used in the research?",
    "What are the limitations mentioned in the study?",
    "What future work is suggested by the authors?"
  ]
}
```

## Deployment

### Backend

1. Set up a production database with PostgreSQL.
2. Deploy to a server using Gunicorn or a similar WSGI server:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

### Frontend

1. Build the production version:
   ```bash
   cd frontend
   npm run build
   ```
2. Deploy the built files to a static hosting service.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
