"""Repository for FewShotExample database operations"""
from typing import List, Optional, Dict
from uuid import UUID
from src.database.models import FewShotExample
from src.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class FewShotExampleRepository:
    """Repository for managing few-shot examples"""

    @staticmethod
    def create_example(
        example_text: str,
        category: str,
        session_id: Optional[str] = None,
        reasoning: Optional[str] = None,
        column_name: Optional[str] = None,
        is_global: bool = False,
        display_order: Optional[int] = None
    ) -> FewShotExample:
        """
        Create a new few-shot example

        Args:
            example_text: Example text to classify
            category: Correct category for this example
            session_id: Optional session ID (None for global examples)
            reasoning: Optional reasoning for classification
            column_name: Optional column name
            is_global: True if example applies to all sessions
            display_order: Optional display order

        Returns:
            Created FewShotExample instance
        """
        with DatabaseConnection.get_session() as session:
            example = FewShotExample(
                example_text=example_text,
                category=category,
                session_id=UUID(session_id) if session_id else None,
                reasoning=reasoning,
                column_name=column_name,
                is_global=is_global,
                display_order=display_order
            )
            session.add(example)
            session.commit()
            session.refresh(example)
            logger.info(f"Created few-shot example: {example.id}")
            return example

    @staticmethod
    def get_session_examples(session_id: str, column_name: Optional[str] = None) -> List[FewShotExample]:
        """
        Get all examples for a session (including global examples)

        Args:
            session_id: Session ID
            column_name: Optional column filter

        Returns:
            List of FewShotExample instances
        """
        with DatabaseConnection.get_session() as session:
            query = session.query(FewShotExample).filter(
                (FewShotExample.session_id == UUID(session_id)) | (FewShotExample.is_global == True)
            )

            if column_name:
                query = query.filter(FewShotExample.column_name == column_name)

            examples = query.order_by(FewShotExample.display_order, FewShotExample.created_at).all()
            return examples

    @staticmethod
    def get_global_examples(column_name: Optional[str] = None) -> List[FewShotExample]:
        """
        Get all global examples

        Args:
            column_name: Optional column filter

        Returns:
            List of global FewShotExample instances
        """
        with DatabaseConnection.get_session() as session:
            query = session.query(FewShotExample).filter(FewShotExample.is_global == True)

            if column_name:
                query = query.filter(FewShotExample.column_name == column_name)

            examples = query.order_by(FewShotExample.display_order, FewShotExample.created_at).all()
            return examples

    @staticmethod
    def delete_example(example_id: str) -> bool:
        """
        Delete a few-shot example

        Args:
            example_id: Example ID to delete

        Returns:
            True if deleted, False if not found
        """
        with DatabaseConnection.get_session() as session:
            example = session.query(FewShotExample).filter(FewShotExample.id == UUID(example_id)).first()

            if example:
                session.delete(example)
                session.commit()
                logger.info(f"Deleted few-shot example: {example_id}")
                return True

            return False

    @staticmethod
    def delete_session_examples(session_id: str) -> int:
        """
        Delete all examples for a session

        Args:
            session_id: Session ID

        Returns:
            Number of examples deleted
        """
        with DatabaseConnection.get_session() as session:
            count = session.query(FewShotExample).filter(
                FewShotExample.session_id == UUID(session_id)
            ).delete()
            session.commit()
            logger.info(f"Deleted {count} few-shot examples for session {session_id}")
            return count

    @staticmethod
    def examples_to_dict(examples: List[FewShotExample]) -> List[Dict]:
        """
        Convert FewShotExample instances to dictionary format for use in prompts

        Args:
            examples: List of FewShotExample instances

        Returns:
            List of dictionaries with text, category, reasoning
        """
        return [
            {
                "text": example.example_text,
                "category": example.category,
                "reasoning": example.reasoning
            }
            for example in examples
        ]

    @staticmethod
    def save_examples_from_session_state(examples: List[Dict], session_id: str, column_name: str) -> int:
        """
        Save examples from session state to database

        Args:
            examples: List of example dictionaries from session state
            session_id: Session ID to associate examples with
            column_name: Column name

        Returns:
            Number of examples saved
        """
        count = 0
        for i, example in enumerate(examples):
            FewShotExampleRepository.create_example(
                example_text=example["text"],
                category=example["category"],
                session_id=session_id,
                reasoning=example.get("reasoning"),
                column_name=column_name,
                is_global=False,
                display_order=i
            )
            count += 1

        logger.info(f"Saved {count} few-shot examples to database for session {session_id}")
        return count
