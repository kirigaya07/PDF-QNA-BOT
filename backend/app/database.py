from sqlalchemy import create_engine # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to a default PostgreSQL URL if not set
    logger.warning("DATABASE_URL not found in environment, using default")
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/pdf_qa_db"

# Create engine with proper PostgreSQL settings
try:
    # Add connect_args to handle PostgreSQL-specific settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Check connection before using it
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=False           # Set to True for debugging SQL
    )
    # Test connection
    with engine.connect() as conn:
        logger.info("Successfully connected to the database!")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise Exception(f"Failed to create database engine: {str(e)}")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 