"""Repository for Session operations"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import desc
from src.database.models import Session
from src.database.connection import DatabaseConnection
from src.database.utils import sanitize_for_db
import logging

logger = logging.getLogger(__name__)


class SessionRepository:
    """Handles all database operations for Sessions"""

    @staticmethod
    def create_session(
        original_filename: Optional[str] = None,
        file_type: Optional[str] = None,
        **kwargs,
    ) -> Session:
        """
        Create a new session

        Args:
            original_filename: Name of uploaded file
            file_type: Type of file (csv | excel)
            **kwargs: Additional session fields

        Returns:
            Created Session object
        """
        with DatabaseConnection.get_session() as db:
            session = Session(
                status="pending_upload",
                original_filename=original_filename,
                file_type=file_type,
                **kwargs,
            )
            db.add(session)
            db.commit()
            db.refresh(session)

            logger.info(f"Created session {session.id}")
            return session

    @staticmethod
    def get_session(session_id: str) -> Optional[Session]:
        """
        Get session by ID

        Args:
            session_id: UUID of session

        Returns:
            Session object or None
        """
        with DatabaseConnection.get_session() as db:
            return db.query(Session).filter(Session.id == session_id).first()

    @staticmethod
    def update_session(session_id: str, **updates) -> Optional[Session]:
        """
        Update session fields

        Args:
            session_id: UUID of session
            **updates: Fields to update

        Returns:
            Updated Session object or None
        """
        with DatabaseConnection.get_session() as db:
            session = db.query(Session).filter(Session.id == session_id).first()

            if session:
                for key, value in updates.items():
                    if hasattr(session, key):
                        # Sanitize JSON fields
                        if key in ['column_metadata', 'categories']:
                            value = sanitize_for_db(value)
                        setattr(session, key, value)

                session.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(session)

                logger.info(f"Updated session {session_id}")
                return session

            logger.warning(f"Session {session_id} not found for update")
            return None

    @staticmethod
    def update_status(session_id: str, status: str) -> Optional[Session]:
        """
        Update session status

        Args:
            session_id: UUID of session
            status: New status

        Returns:
            Updated Session object or None
        """
        return SessionRepository.update_session(session_id, status=status)

    @staticmethod
    def save_categories(
        session_id: str, categories: List[Dict], num_categories: Optional[int] = None
    ) -> Optional[Session]:
        """
        Save discovered categories to session

        Args:
            session_id: UUID of session
            categories: List of category definitions
            num_categories: Number of categories

        Returns:
            Updated Session object or None
        """
        return SessionRepository.update_session(
            session_id,
            categories=categories,
            num_categories=num_categories or len(categories),
            status="categories_discovered",
        )

    @staticmethod
    def save_column_selection(
        session_id: str, selected_column: str, column_metadata: Optional[Dict] = None
    ) -> Optional[Session]:
        """
        Save selected column for classification

        Args:
            session_id: UUID of session
            selected_column: Name of selected column
            column_metadata: Metadata about all columns

        Returns:
            Updated Session object or None
        """
        updates = {"selected_column": selected_column}
        if column_metadata:
            updates["column_metadata"] = column_metadata

        return SessionRepository.update_session(session_id, **updates)

    @staticmethod
    def list_recent_sessions(limit: int = 10) -> List[Session]:
        """
        Get recent sessions

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of Session objects
        """
        with DatabaseConnection.get_session() as db:
            return (
                db.query(Session)
                .order_by(desc(Session.created_at))
                .limit(limit)
                .all()
            )

    @staticmethod
    def get_latest_session() -> Optional[Session]:
        """
        Get the most recent session

        Returns:
            Latest Session object or None
        """
        sessions = SessionRepository.list_recent_sessions(limit=1)
        return sessions[0] if sessions else None

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """
        Delete a session and all related data

        Args:
            session_id: UUID of session

        Returns:
            True if deleted, False if not found
        """
        with DatabaseConnection.get_session() as db:
            session = db.query(Session).filter(Session.id == session_id).first()

            if session:
                db.delete(session)
                db.commit()
                logger.info(f"Deleted session {session_id}")
                return True

            logger.warning(f"Session {session_id} not found for deletion")
            return False

    @staticmethod
    def cleanup_expired_sessions() -> int:
        """
        Delete expired sessions

        Returns:
            Number of deleted sessions
        """
        with DatabaseConnection.get_session() as db:
            now = datetime.utcnow()
            expired = db.query(Session).filter(Session.expires_at <= now).all()

            count = len(expired)
            for session in expired:
                db.delete(session)

            db.commit()
            logger.info(f"Cleaned up {count} expired sessions")
            return count

    @staticmethod
    def set_expiration(session_id: str, hours: int = 24) -> Optional[Session]:
        """
        Set session expiration time

        Args:
            session_id: UUID of session
            hours: Hours until expiration

        Returns:
            Updated Session object or None
        """
        expires_at = datetime.utcnow() + timedelta(hours=hours)
        return SessionRepository.update_session(session_id, expires_at=expires_at)
