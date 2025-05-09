"""
Fix database setup and ensure tables are created properly.
"""
import os
import sys
from sqlalchemy import inspect, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import after logging setup
from app.database import SessionLocal, engine, Base
from app import models

def check_db_connection():
    """Verify database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful!")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

def create_tables():
    """Create database tables if they don't exist."""
    try:
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {str(e)}")
        return False

def check_tables():
    """Check if all required tables exist."""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        logger.info(f"📋 Existing tables: {existing_tables}")
        
        required_tables = ['documents']
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            logger.error(f"❌ Missing tables: {missing_tables}")
            return False
        else:
            logger.info("✅ All required tables exist!")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to check tables: {str(e)}")
        return False

def check_table_columns():
    """Check if table columns are correctly defined."""
    try:
        inspector = inspect(engine)
        
        # Check documents table columns
        columns = inspector.get_columns('documents')
        column_names = [col['name'] for col in columns]
        logger.info(f"📋 Columns in documents table: {column_names}")
        
        required_columns = ['id', 'filename', 'original_filename', 'upload_date', 'file_path', 'text_content']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            logger.error(f"❌ Missing columns in documents table: {missing_columns}")
            return False
        else:
            logger.info("✅ All required columns exist in documents table!")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to check table columns: {str(e)}")
        return False

def test_document_insertion():
    """Test if we can insert a document record."""
    db = SessionLocal()
    try:
        # Create a test document
        test_doc = models.Document(
            filename="test_document.pdf",
            original_filename="test.pdf",
            upload_date="2023-01-01 00:00:00",
            file_path="/tmp/test.pdf",
            text_content="This is a test document content."
        )
        
        # Add it to the session
        db.add(test_doc)
        db.commit()
        db.refresh(test_doc)
        
        logger.info(f"✅ Successfully inserted test document with ID: {test_doc.id}")
        
        # Try to retrieve it
        retrieved_doc = db.query(models.Document).filter(models.Document.id == test_doc.id).first()
        
        if retrieved_doc:
            logger.info("✅ Successfully retrieved test document!")
            
            # Clean up - delete the test document
            db.delete(retrieved_doc)
            db.commit()
            
            # Verify deletion
            check = db.query(models.Document).filter(models.Document.id == test_doc.id).first()
            if check:
                logger.warning("⚠️ Failed to delete test document")
            else:
                logger.info("✅ Successfully deleted test document!")
            
            return True
        else:
            logger.error("❌ Failed to retrieve test document!")
            return False
    except Exception as e:
        logger.error(f"❌ Error during document insertion test: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main function to fix database issues."""
    logger.info("🔧 Starting database repair process...")
    
    # Check connection
    if not check_db_connection():
        logger.error("❌ Cannot proceed without database connection")
        return False
    
    # Create tables if needed
    create_tables()
    
    # Check if tables exist
    if not check_tables():
        logger.error("❌ Required tables are missing even after creation attempt!")
        return False
    
    # Check table columns
    if not check_table_columns():
        logger.error("❌ Table columns are not correctly defined!")
        return False
    
    # Test document insertion
    if not test_document_insertion():
        logger.error("❌ Failed to insert and retrieve a test document!")
        return False
    
    logger.info("✅ Database setup verified and fixed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        logger.error("❌ Database repair failed!")
        sys.exit(1)
    else:
        logger.info("🎉 Database is now ready to use!")
        sys.exit(0) 