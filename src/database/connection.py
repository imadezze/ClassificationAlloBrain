"""Database connection management"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from src.config import Config
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages database connections and session lifecycle"""

    _engine = None
    _session_factory = None

    @classmethod
    def get_engine(cls):
        """Get or create database engine (singleton pattern)"""
        if cls._engine is None:
            logger.info("Creating database engine")

            cls._engine = create_engine(
                Config.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=Config.DB_POOL_SIZE,
                max_overflow=Config.DB_MAX_OVERFLOW,
                pool_timeout=Config.DB_POOL_TIMEOUT,
                pool_recycle=Config.DB_POOL_RECYCLE,
                pool_pre_ping=True,  # Verify connections before using
                echo=Config.DB_ECHO,  # Log SQL queries (for debugging)
            )

            # Add connection lifecycle logging
            @event.listens_for(cls._engine, "connect")
            def receive_connect(dbapi_conn, connection_record):
                logger.debug("Database connection established")

            @event.listens_for(cls._engine, "close")
            def receive_close(dbapi_conn, connection_record):
                logger.debug("Database connection closed")

        return cls._engine

    @classmethod
    def get_session_factory(cls):
        """Get or create session factory"""
        if cls._session_factory is None:
            engine = cls.get_engine()
            cls._session_factory = scoped_session(
                sessionmaker(
                    bind=engine,
                    autocommit=False,
                    autoflush=False,
                    expire_on_commit=False,
                )
            )
        return cls._session_factory

    @classmethod
    @contextmanager
    def get_session(cls):
        """
        Context manager for database sessions

        Usage:
            with DatabaseConnection.get_session() as session:
                session.query(Model).all()
        """
        session_factory = cls.get_session_factory()
        session = session_factory()

        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()

    @classmethod
    def init_db(cls):
        """Initialize database (create tables if they don't exist)"""
        from src.database.models import Base

        logger.info("Initializing database schema")
        engine = cls.get_engine()
        Base.metadata.create_all(engine)
        logger.info("Database schema initialized")

    @classmethod
    def close_all_connections(cls):
        """Close all database connections (cleanup)"""
        if cls._session_factory:
            cls._session_factory.remove()

        if cls._engine:
            cls._engine.dispose()
            logger.info("All database connections closed")

    @classmethod
    def test_connection(cls) -> bool:
        """
        Test database connectivity

        Returns:
            True if connection successful, False otherwise
        """
        try:
            engine = cls.get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
