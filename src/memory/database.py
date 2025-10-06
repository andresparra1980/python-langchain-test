from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
from config import config
from src.memory.models import Base


class Database:
    """Database connection and session management"""
    
    def __init__(self, database_url: str = None):
        """
        Initialize database connection.
        
        Args:
            database_url: SQLAlchemy database URL. If None, uses config.DATABASE_URL
        """
        self.database_url = database_url or config.DATABASE_URL
        
        # Create engine with appropriate settings
        if self.database_url.startswith("sqlite"):
            # SQLite-specific configuration
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            self.engine = create_engine(self.database_url, echo=False)
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Initialize database (create tables)
        self.init_db()
    
    def init_db(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
        print(f"✓ Database initialized at: {self.database_url}")
    
    def drop_all(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
        print("⚠️  All database tables dropped")
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy Session object
        """
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.
        
        Usage:
            with db.session_scope() as session:
                session.add(topic)
                # Changes are automatically committed
        
        Yields:
            SQLAlchemy Session object
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()
        print("✓ Database connection closed")


# Global database instance
_db_instance = None


def get_database() -> Database:
    """
    Get or create the global database instance.
    
    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def reset_database():
    """Reset the global database instance (useful for testing)"""
    global _db_instance
    if _db_instance:
        _db_instance.close()
    _db_instance = None
