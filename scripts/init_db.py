# Indian Law RAG Chatbot - Database Initialization
"""
Initialize PostgreSQL database tables.

Usage:
    python scripts/init_db.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

import logging
from app.db.database import init_db, engine, check_db_connection
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Initialize the database."""
    print("\n" + "=" * 60)
    print("Indian Law RAG Chatbot - Database Initialization")
    print("=" * 60 + "\n")
    
    print(f"Database URL: {settings.database_url[:50]}...")
    
    # Check connection
    print("\nChecking database connection...")
    if not check_db_connection():
        print("✗ Could not connect to database!")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check DATABASE_URL in .env file")
        print("3. Run: docker-compose up -d (for Docker setup)")
        return
    
    print("✓ Database connection successful!")
    
    # Create tables
    print("\nCreating database tables...")
    try:
        init_db()
        print("✓ All tables created successfully!")
        
        print("\nTables created:")
        print("  - users")
        print("  - chat_sessions")
        print("  - chat_messages")
        print("  - query_logs")
        print("  - application_logs")
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
