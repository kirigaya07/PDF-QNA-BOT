# PDF Q&A Application - Architecture Document

## 1. High-Level Design (HLD)

### 1.1 System Overview

The PDF Q&A application is a full-stack web application that allows users to upload PDF documents, ask questions about their content, and receive AI-generated answers. The system uses natural language processing to understand and answer questions based on document content.

### 1.2 Architecture Diagram

```
┌────────────────┐       ┌────────────────────────────────────┐
│                │       │                                    │
│                │       │  ┌─────────────┐   ┌────────────┐  │
│   React        │◄─────▶│  │             │   │            │  │
│   Frontend     │       │  │  FastAPI    │◄─▶│ PostgreSQL │  │
│                │       │  │  Backend    │   │ Database   │  │
│                │       │  │             │   │            │  │
└────────────────┘       │  └──────┬──────┘   └────────────┘  │
                         │         │                          │
                         │         ▼                          │
                         │  ┌─────────────┐    ┌───────────┐  │
                         │  │  Gemini API │    │ PDF Files │  │
                         │  │  (Google)   │    │ Storage   │  │
                         │  └─────────────┘    └───────────┘  │
                         │                                    │
                         └────────────────────────────────────┘
```

### 1.3 Key Components

1. **Frontend (React)**

   - User interface for PDF upload, document viewing, and question/answer interaction
   - Chatbot-style interface for Q&A interaction
   - Suggested questions feature

2. **Backend (FastAPI)**

   - REST API endpoints for all application features
   - PDF processing and text extraction
   - Integration with AI models for question answering
   - Database operations

3. **Database (PostgreSQL)**

   - Storage of document metadata
   - Storage of extracted document text content

4. **External Services**

   - Google's Gemini API for natural language processing and question answering

5. **Storage**
   - Local file storage for uploaded PDF documents

### 1.4 System Flow

1. User uploads a PDF document through the frontend interface
2. Backend processes the PDF, extracts text, and saves to database
3. User views the document and asks questions or selects suggested questions
4. Backend forwards questions to the Gemini API along with document context
5. Gemini API generates answers based on document content
6. Answers are displayed to the user in a conversational interface
7. User can continue asking questions or delete documents as needed

## 2. Low-Level Design (LLD)

### 2.1 Frontend Components

#### 2.1.1 Main Components

| Component          | Description                                              |
| ------------------ | -------------------------------------------------------- |
| `Home.tsx`         | Landing page with document list and upload functionality |
| `DocumentView.tsx` | Chatbot interface for interacting with documents         |
| `PDFUploader.tsx`  | Component for uploading PDF files                        |
| `Navbar.tsx`       | Navigation component                                     |

#### 2.1.2 State Management

The application uses React's built-in state management with hooks:

- `useState` for local component state
- `useEffect` for side effects and data fetching
- `useRef` for DOM references
- `useNavigate` for navigation between pages

#### 2.1.3 API Communication

- Fetch API for communication with the backend
- Endpoints include:
  - `/documents/` - List, get, create and delete documents
  - `/ask/` - Submit questions and get answers
  - `/documents/{id}/suggested-questions` - Get AI-generated question suggestions

### 2.2 Backend Components

#### 2.2.1 Core Modules

| Module             | Description                                      |
| ------------------ | ------------------------------------------------ |
| `main.py`          | FastAPI application and endpoint definitions     |
| `models.py`        | SQLAlchemy ORM models for database tables        |
| `schemas.py`       | Pydantic schemas for request/response validation |
| `database.py`      | Database connection and session management       |
| `pdf_processor.py` | PDF handling and text extraction                 |
| `qa_engine.py`     | Integration with Gemini API for Q&A              |

#### 2.2.2 Database Schema

```
┌───────────────────┐
│ Document          │
├───────────────────┤
│ id (PK)           │
│ filename          │
│ original_filename │
│ upload_date       │
│ file_path         │
│ text_content      │
└───────────────────┘
```

#### 2.2.3 API Endpoints

| Endpoint                              | Method | Description                     |
| ------------------------------------- | ------ | ------------------------------- |
| `/upload/`                            | POST   | Upload PDF document             |
| `/documents/`                         | GET    | List all documents              |
| `/documents/{id}`                     | GET    | Get document details            |
| `/documents/{id}`                     | DELETE | Delete a document               |
| `/ask/`                               | POST   | Ask a question about a document |
| `/documents/{id}/suggested-questions` | GET    | Get AI-generated questions      |

### 2.3 PDF Processing Pipeline

1. **Upload Processing**

   - Validate file is PDF format
   - Save file to disk with unique filename
   - Extract text content using PDF processor

2. **Text Extraction**

   - Parse PDF document
   - Extract text content
   - Store in database alongside document metadata

3. **Question Answering**
   - Split document text into chunks if necessary (for large documents)
   - Format prompt with question and document context
   - Send to Gemini API for processing
   - Return formatted answer to user

### 2.4 AI Integration Details

#### 2.4.1 Gemini API Integration

- Model: `gemini-1.5-flash` for question answering
- Context-aware prompting to ensure answers are based on document content
- Error handling for API limits and failures
- Text chunk management for documents exceeding token limits

#### 2.4.2 Question Generation

- Analysis of document content to generate relevant questions
- Prioritization of key information and topics from the document
- Mix of factual and analytical question types

### 2.5 Security Considerations

1. **Input Validation**

   - File type validation for uploads
   - Request body validation using Pydantic schemas

2. **CORS Configuration**

   - Configured to allow only the frontend application origin

3. **Error Handling**
   - Comprehensive error handling with appropriate HTTP status codes
   - Detailed logging for debugging and monitoring

## 3. Technology Stack

### 3.1 Frontend

- React (TypeScript)
- Chakra UI for component styling
- React Router for navigation
- Emotion for advanced styling

### 3.2 Backend

- Python 3.x
- FastAPI web framework
- SQLAlchemy ORM
- Alembic for database migrations
- Langchain for text processing
- Google Generative AI SDK

### 3.3 Database

- PostgreSQL

### 3.4 External Services

- Google Gemini API for natural language processing

### 3.5 Development & Deployment

- Environment configuration using dotenv
- Local development setup with separate frontend and backend servers

## 4. Future Enhancements

1. **Authentication & Authorization**

   - User accounts and authentication
   - Role-based access control

2. **Document Management**

   - Folder organization for documents
   - Document tagging and categorization
   - Document search functionality

3. **Performance Improvements**

   - Document text vectorization and semantic search
   - Response caching for common questions
   - Background processing for large documents

4. **Enhanced AI Features**
   - Multiple AI model support
   - Document summarization
   - Key information extraction
   - Multi-document Q&A
