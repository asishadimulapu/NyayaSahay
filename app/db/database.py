# Indian Law RAG Chatbot - Database Connection
"""
PostgreSQL database connection and session management using SQLAlchemy.
Provides both sync and async database capabilities.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# =============================================================================
# SQLAlchemy Base Class
# =============================================================================
Base = declarative_base()

# =============================================================================
# Database Engine Configuration
# =============================================================================
# Engine configuration with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=5,           # Number of connections to keep open
    max_overflow=10,       # Additional connections when pool is full
    pool_timeout=30,       # Seconds to wait for available connection
    pool_recycle=1800,     # Recycle connections after 30 minutes
    echo=settings.debug,   # Log SQL queries in debug mode
)


# =============================================================================
# Session Factory
# =============================================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =============================================================================
# Database Event Listeners
# =============================================================================
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Event listener for connection establishment.
    Can be used for connection-level configuration.
    """
    logger.debug("Database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """
    Event listener for connection checkout from pool.
    Useful for monitoring connection usage.
    """
    logger.debug("Connection checked out from pool")


# =============================================================================
# Dependency Injection for FastAPI
# =============================================================================
def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
            
    Viva Explanation:
    - Generator pattern ensures proper cleanup
    - Session is automatically closed after request
    - Works with FastAPI's dependency injection system
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# Database Initialization
# =============================================================================
def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in the models.
    
    Viva Explanation:
    - Uses SQLAlchemy's create_all() method
    - Safe to call multiple times (won't recreate existing tables)
    - Should be called on application startup
    """
    from app.db import models  # noqa: F401 - Import models to register them
    
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
