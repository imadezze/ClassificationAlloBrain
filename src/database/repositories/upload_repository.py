"""Repository for Upload operations"""
from typing import Optional, List
from datetime import datetime
from src.database.models import Upload
from src.database.connection import DatabaseConnection
from src.database.utils import sanitize_for_db
import logging

logger = logging.getLogger(__name__)


class UploadRepository:
    """Handles all database operations for Uploads"""

    @staticmethod
    def create_upload(
        session_id: str,
        original_filename: str,
        file_type: str,
        file_size_bytes: int,
        file_hash: str,
        row_count: int,
        column_count: int,
        **kwargs,
    ) -> Upload:
        """
        Create an upload record

        Args:
            session_id: UUID of parent session
            original_filename: Original filename
            file_type: Type of file (csv | excel)
            file_size_bytes: File size in bytes
            file_hash: MD5 hash of file
            row_count: Number of rows
            column_count: Number of columns
            **kwargs: Additional fields (encoding, sheets, column_metadata, etc.)

        Returns:
            Created Upload object
        """
        with DatabaseConnection.get_session() as db:
            # Sanitize JSONB fields
            if "column_metadata" in kwargs:
                kwargs["column_metadata"] = sanitize_for_db(kwargs["column_metadata"])
            if "sheets" in kwargs:
                kwargs["sheets"] = sanitize_for_db(kwargs["sheets"])

            upload = Upload(
                session_id=session_id,
                original_filename=original_filename,
                file_type=file_type,
                file_size_bytes=file_size_bytes,
                file_hash=file_hash,
                row_count=row_count,
                column_count=column_count,
                status="uploaded",
                **kwargs,
            )
            db.add(upload)
            db.commit()
            db.refresh(upload)

            logger.info(f"Created upload {upload.id} for session {session_id}")
            return upload

    @staticmethod
    def get_upload(upload_id: str) -> Optional[Upload]:
        """Get upload by ID"""
        with DatabaseConnection.get_session() as db:
            return db.query(Upload).filter(Upload.id == upload_id).first()

    @staticmethod
    def get_session_uploads(session_id: str) -> List[Upload]:
        """Get all uploads for a session"""
        with DatabaseConnection.get_session() as db:
            return (
                db.query(Upload)
                .filter(Upload.session_id == session_id)
                .order_by(Upload.uploaded_at)
                .all()
            )

    @staticmethod
    def get_by_session(session_id: str) -> Optional[Upload]:
        """
        Get the most recent upload for a session

        Args:
            session_id: UUID of session

        Returns:
            Most recent Upload object or None
        """
        with DatabaseConnection.get_session() as db:
            return (
                db.query(Upload)
                .filter(Upload.session_id == session_id)
                .order_by(Upload.uploaded_at.desc())
                .first()
            )

    @staticmethod
    def update_upload_status(
        upload_id: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> Optional[Upload]:
        """
        Update upload status

        Args:
            upload_id: UUID of upload
            status: New status (uploaded | processing | processed | error)
            error_message: Error message if status is error

        Returns:
            Updated Upload object or None
        """
        with DatabaseConnection.get_session() as db:
            upload = db.query(Upload).filter(Upload.id == upload_id).first()

            if upload:
                upload.status = status
                if error_message:
                    upload.error_message = error_message
                if status == "processed":
                    upload.processed_at = datetime.utcnow()

                db.commit()
                db.refresh(upload)

                logger.info(f"Updated upload {upload_id} status to {status}")
                return upload

            logger.warning(f"Upload {upload_id} not found for status update")
            return None

    @staticmethod
    def find_by_hash(file_hash: str) -> Optional[Upload]:
        """
        Find upload by file hash (for deduplication)

        Args:
            file_hash: MD5 hash of file

        Returns:
            Upload object or None
        """
        with DatabaseConnection.get_session() as db:
            return db.query(Upload).filter(Upload.file_hash == file_hash).first()
