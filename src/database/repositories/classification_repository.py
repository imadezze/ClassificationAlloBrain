"""Repository for Classification operations"""
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy import func
from src.database.models import Classification
from src.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class ClassificationRepository:
    """Handles all database operations for Classifications"""

    @staticmethod
    def create_classification(
        session_id: str,
        input_text: str,
        predicted_category: str,
        success: bool = True,
        **kwargs,
    ) -> Classification:
        """
        Create a classification record

        Args:
            session_id: UUID of parent session
            input_text: Original text classified
            predicted_category: Predicted category
            success: Whether classification succeeded
            **kwargs: Additional fields (confidence, row_index, etc.)

        Returns:
            Created Classification object
        """
        with DatabaseConnection.get_session() as db:
            classification = Classification(
                session_id=session_id,
                input_text=input_text,
                predicted_category=predicted_category,
                success=success,
                **kwargs,
            )
            db.add(classification)
            db.commit()
            db.refresh(classification)

            return classification

    @staticmethod
    def bulk_create_classifications(
        classifications_data: List[Dict],
    ) -> List[Classification]:
        """
        Bulk insert classifications (more efficient for large datasets)

        Args:
            classifications_data: List of classification dictionaries

        Returns:
            List of created Classification objects
        """
        with DatabaseConnection.get_session() as db:
            classifications = [
                Classification(**data) for data in classifications_data
            ]

            db.bulk_save_objects(classifications, return_defaults=True)
            db.commit()

            logger.info(f"Bulk created {len(classifications)} classifications")
            return classifications

    @staticmethod
    def get_classification(classification_id: str) -> Optional[Classification]:
        """
        Get classification by ID

        Args:
            classification_id: UUID of classification

        Returns:
            Classification object or None
        """
        with DatabaseConnection.get_session() as db:
            return (
                db.query(Classification)
                .filter(Classification.id == classification_id)
                .first()
            )

    @staticmethod
    def get_session_classifications(session_id: str) -> List[Classification]:
        """
        Get all classifications for a session

        Args:
            session_id: UUID of session

        Returns:
            List of Classification objects
        """
        with DatabaseConnection.get_session() as db:
            return (
                db.query(Classification)
                .filter(Classification.session_id == session_id)
                .order_by(Classification.created_at)
                .all()
            )

    @staticmethod
    def get_category_distribution(session_id: str) -> Dict[str, int]:
        """
        Get distribution of categories for a session

        Args:
            session_id: UUID of session

        Returns:
            Dictionary mapping category names to counts
        """
        with DatabaseConnection.get_session() as db:
            results = (
                db.query(
                    Classification.predicted_category,
                    func.count(Classification.id).label("count"),
                )
                .filter(Classification.session_id == session_id)
                .filter(Classification.success == True)
                .group_by(Classification.predicted_category)
                .all()
            )

            return {category: count for category, count in results}

    @staticmethod
    def get_statistics(session_id: str) -> Dict:
        """
        Get classification statistics for a session

        Args:
            session_id: UUID of session

        Returns:
            Dictionary with statistics
        """
        with DatabaseConnection.get_session() as db:
            total = (
                db.query(func.count(Classification.id))
                .filter(Classification.session_id == session_id)
                .scalar()
            )

            successful = (
                db.query(func.count(Classification.id))
                .filter(Classification.session_id == session_id)
                .filter(Classification.success == True)
                .scalar()
            )

            failed = total - successful

            avg_execution_time = (
                db.query(func.avg(Classification.execution_time_ms))
                .filter(Classification.session_id == session_id)
                .filter(Classification.success == True)
                .scalar()
            )

            total_tokens = (
                db.query(func.sum(Classification.tokens_used))
                .filter(Classification.session_id == session_id)
                .filter(Classification.success == True)
                .scalar()
            )

            return {
                "total": total or 0,
                "successful": successful or 0,
                "failed": failed or 0,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "avg_execution_time_ms": float(avg_execution_time or 0),
                "total_tokens_used": int(total_tokens or 0),
            }

    @staticmethod
    def delete_session_classifications(session_id: str) -> int:
        """
        Delete all classifications for a session

        Args:
            session_id: UUID of session

        Returns:
            Number of deleted classifications
        """
        with DatabaseConnection.get_session() as db:
            count = (
                db.query(Classification)
                .filter(Classification.session_id == session_id)
                .delete()
            )
            db.commit()

            logger.info(f"Deleted {count} classifications for session {session_id}")
            return count
