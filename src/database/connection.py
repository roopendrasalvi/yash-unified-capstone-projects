"""
Database Connection
Manages database connections (PostgreSQL/Supabase and SQLite)
"""

from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from config.config_loader import get_database_config
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self, use_sqlite: bool = False):
        """
        Initialize database connection
        
        Args:
            use_sqlite: Whether to use SQLite instead of PostgreSQL
        """
        self.db_config = get_database_config()
        self.use_sqlite = use_sqlite
        self.engine = None
        self.SessionLocal = None
        self._setup_connection()
    
    def _setup_connection(self):
        """Setup database connection"""
        try:
            if self.use_sqlite:
                # SQLite configuration
                sqlite_config = self.db_config.get("sqlite", {})
                database_url = sqlite_config.get("database_url", "sqlite:///./email_assistant.db")
            else:
                # PostgreSQL/Supabase configuration
                postgres_config = self.db_config.get("postgresql", {})
                
                # Build connection URL
                user = postgres_config.get("user")
                password = postgres_config.get("password")
                host = postgres_config.get("host")
                port = postgres_config.get("port", 5432)
                database = postgres_config.get("database")
                
                database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            
            # Create engine
            self.engine = create_engine(
                database_url,
                echo=False,  # Set to True for SQL logging
                pool_pre_ping=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database connection established ({'SQLite' if self.use_sqlite else 'PostgreSQL'})")
            
        except Exception as e:
            logger.error(f"Error setting up database connection: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """
        Get a database session
        
        Returns:
            SQLAlchemy Session
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database connection not initialized")
        
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all tables in the database"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
    
    def drop_tables(self):
        """Drop all tables in the database"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped")
        except Exception as e:
            logger.error(f"Error dropping tables: {str(e)}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Dependency for FastAPI
def get_db():
    """
    Dependency function for FastAPI to get database session
    
    Yields:
        Database session
    """
    db_connection = DatabaseConnection()
    db = db_connection.get_session()
    try:
        yield db
    finally:
        db.close()

