"""Repository for category history operations"""
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.models import CategoryHistory
from src.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class CategoryHistoryRepository:
    """Repository for managing category history records"""

    @staticmethod
    def create_history_entry(
        session_id: str,
        categories: List[dict],
        change_type: str = "initial_discovery",
        user_feedback: Optional[str] = None,
        change_description: Optional[str] = None
    ) -> CategoryHistory:
        """
        Create a new category history entry

        Args:
            session_id: Session UUID
            categories: List of category definitions
            change_type: Type of change (initial_discovery, user_edit, llm_refinement)
            user_feedback: Optional feedback that triggered the refinement
            change_description: Description of what changed

        Returns:
            Created CategoryHistory object
        """
        with DatabaseConnection.get_session() as db_session:
            # Get next version number for this session
            latest_version = (
                db_session.query(CategoryHistory.version)
                .filter(CategoryHistory.session_id == session_id)
                .order_by(CategoryHistory.version.desc())
                .first()
            )
            version = (latest_version[0] + 1) if latest_version else 1

            history = CategoryHistory(
                session_id=session_id,
                version=version,
                categories=categories,
                change_type=change_type,
                user_feedback=user_feedback,
                change_description=change_description
            )

            db_session.add(history)
            db_session.commit()
            db_session.refresh(history)

            logger.info(f"Created category history entry: {history.id} version {version} ({change_type})")
            return history

    @staticmethod
    def get_session_history(session_id: str) -> List[CategoryHistory]:
        """
        Get all category history for a session, ordered by creation time

        Args:
            session_id: Session UUID

        Returns:
            List of CategoryHistory objects
        """
        with DatabaseConnection.get_session() as db_session:
            history = (
                db_session.query(CategoryHistory)
                .filter(CategoryHistory.session_id == session_id)
                .order_by(CategoryHistory.created_at)
                .all()
            )

            return history

    @staticmethod
    def get_latest_categories(session_id: str) -> Optional[CategoryHistory]:
        """
        Get the most recent category definition for a session

        Args:
            session_id: Session UUID

        Returns:
            Latest CategoryHistory object or None
        """
        with DatabaseConnection.get_session() as db_session:
            latest = (
                db_session.query(CategoryHistory)
                .filter(CategoryHistory.session_id == session_id)
                .order_by(CategoryHistory.created_at.desc())
                .first()
            )

            return latest

    @staticmethod
    def count_refinements(session_id: str) -> int:
        """
        Count how many times categories were refined for a session

        Args:
            session_id: Session UUID

        Returns:
            Number of refinements
        """
        with DatabaseConnection.get_session() as db_session:
            count = (
                db_session.query(CategoryHistory)
                .filter(
                    CategoryHistory.session_id == session_id,
                    CategoryHistory.change_type == "llm_refinement"
                )
                .count()
            )

            return count

    @staticmethod
    def get_history_by_type(session_id: str, change_type: str) -> List[CategoryHistory]:
        """
        Get category history filtered by change type

        Args:
            session_id: Session UUID
            change_type: Type of change to filter by

        Returns:
            List of CategoryHistory objects
        """
        with DatabaseConnection.get_session() as db_session:
            history = (
                db_session.query(CategoryHistory)
                .filter(
                    CategoryHistory.session_id == session_id,
                    CategoryHistory.change_type == change_type
                )
                .order_by(CategoryHistory.created_at)
                .all()
            )

            return history

    @staticmethod
    def delete_session_history(session_id: str) -> bool:
        """
        Delete all category history for a session

        Args:
            session_id: Session UUID

        Returns:
            True if successful
        """
        try:
            with DatabaseConnection.get_session() as db_session:
                deleted = (
                    db_session.query(CategoryHistory)
                    .filter(CategoryHistory.session_id == session_id)
                    .delete()
                )

                db_session.commit()
                logger.info(f"Deleted {deleted} category history records for session {session_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting category history: {str(e)}")
            return False
