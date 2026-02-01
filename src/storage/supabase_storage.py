"""Supabase Storage integration for file uploads"""
from supabase import create_client, Client
from src.config import Config
import logging
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class SupabaseStorage:
    """Handles file storage operations with Supabase Storage"""

    _client: Optional[Client] = None
    BUCKET_NAME = "uploads"

    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client (singleton) using service role key"""
        if cls._client is None:
            # Ensure URL ends with /
            supabase_url = Config.SUPABASE_URL.rstrip('/') + '/'

            # Use service role key to bypass RLS for storage operations
            cls._client = create_client(
                supabase_url,
                Config.SUPABASE_SECRET_KEY  # Use service role key
            )
        return cls._client

    @classmethod
    def upload_file(
        cls,
        file_bytes: bytes,
        session_id: str,
        filename: str,
        file_type: str = "application/octet-stream"
    ) -> Dict[str, str]:
        """
        Upload file to Supabase Storage

        Args:
            file_bytes: File content as bytes
            session_id: Session UUID (used for folder structure)
            filename: Original filename
            file_type: MIME type of file

        Returns:
            Dictionary with path and url

        Raises:
            Exception: If upload fails
        """
        try:
            # Ensure bucket exists
            cls.create_bucket_if_not_exists()

            client = cls.get_client()

            # Create path: session_id/filename
            file_path = f"{session_id}/{filename}"

            logger.info(f"Uploading file to Supabase Storage: {file_path}")

            # Upload file
            client.storage.from_(cls.BUCKET_NAME).upload(
                path=file_path,
                file=file_bytes,
                file_options={
                    "content-type": file_type,
                    "upsert": "true"  # Overwrite if exists
                }
            )

            # Get public URL
            url = client.storage.from_(cls.BUCKET_NAME).get_public_url(file_path)

            logger.info(f"File uploaded successfully: {file_path}")

            return {
                "path": file_path,
                "url": url,
                "bucket": cls.BUCKET_NAME
            }

        except Exception as e:
            logger.error(f"Error uploading file to Supabase: {str(e)}")
            raise Exception(f"Failed to upload file to storage: {str(e)}")

    @classmethod
    def download_file(cls, session_id: str, filename: str) -> bytes:
        """
        Download file from Supabase Storage

        Args:
            session_id: Session UUID
            filename: Filename to download

        Returns:
            File content as bytes

        Raises:
            Exception: If download fails
        """
        try:
            client = cls.get_client()
            file_path = f"{session_id}/{filename}"

            logger.info(f"Downloading file from Supabase Storage: {file_path}")

            response = client.storage.from_(cls.BUCKET_NAME).download(file_path)

            logger.info(f"File downloaded successfully: {file_path}")
            return response

        except Exception as e:
            logger.error(f"Error downloading file from Supabase: {str(e)}")
            raise Exception(f"Failed to download file from storage: {str(e)}")

    @classmethod
    def delete_file(cls, session_id: str, filename: str) -> bool:
        """
        Delete file from Supabase Storage

        Args:
            session_id: Session UUID
            filename: Filename to delete

        Returns:
            True if deleted successfully

        Raises:
            Exception: If deletion fails
        """
        try:
            client = cls.get_client()
            file_path = f"{session_id}/{filename}"

            logger.info(f"Deleting file from Supabase Storage: {file_path}")

            client.storage.from_(cls.BUCKET_NAME).remove([file_path])

            logger.info(f"File deleted successfully: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file from Supabase: {str(e)}")
            raise Exception(f"Failed to delete file from storage: {str(e)}")

    @classmethod
    def delete_session_files(cls, session_id: str) -> bool:
        """
        Delete all files for a session

        Args:
            session_id: Session UUID

        Returns:
            True if deleted successfully
        """
        try:
            client = cls.get_client()

            # List all files in session folder
            files = client.storage.from_(cls.BUCKET_NAME).list(session_id)

            if not files:
                logger.info(f"No files found for session {session_id}")
                return True

            # Delete all files
            file_paths = [f"{session_id}/{f['name']}" for f in files]
            client.storage.from_(cls.BUCKET_NAME).remove(file_paths)

            logger.info(f"Deleted {len(file_paths)} files for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting session files from Supabase: {str(e)}")
            raise Exception(f"Failed to delete session files: {str(e)}")

    @classmethod
    def get_file_url(cls, session_id: str, filename: str) -> str:
        """
        Get public URL for a file

        Args:
            session_id: Session UUID
            filename: Filename

        Returns:
            Public URL for the file
        """
        client = cls.get_client()
        file_path = f"{session_id}/{filename}"
        return client.storage.from_(cls.BUCKET_NAME).get_public_url(file_path)

    @classmethod
    def check_bucket_exists(cls) -> bool:
        """
        Check if the uploads bucket exists

        Returns:
            True if bucket exists
        """
        try:
            client = cls.get_client()
            buckets = client.storage.list_buckets()

            # Handle different response types
            if isinstance(buckets, list):
                return any(b.get('name') == cls.BUCKET_NAME if isinstance(b, dict) else b.name == cls.BUCKET_NAME for b in buckets)
            elif hasattr(buckets, '__iter__'):
                return any(getattr(b, 'name', b.get('name') if isinstance(b, dict) else None) == cls.BUCKET_NAME for b in buckets)

            return False
        except Exception as e:
            logger.error(f"Error checking bucket: {str(e)}")
            return False

    @classmethod
    def create_bucket_if_not_exists(cls) -> bool:
        """
        Create the uploads bucket if it doesn't exist

        Returns:
            True if bucket exists or was created successfully
        """
        try:
            if cls.check_bucket_exists():
                logger.info(f"Bucket '{cls.BUCKET_NAME}' already exists")
                return True

            client = cls.get_client()
            logger.info(f"Creating bucket '{cls.BUCKET_NAME}'")

            # Create bucket as public for easy access
            client.storage.create_bucket(
                cls.BUCKET_NAME,
                options={
                    "public": True,
                    "file_size_limit": 52428800,  # 50MB
                    "allowed_mime_types": [
                        "text/csv",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "application/vnd.ms-excel",
                    ]
                }
            )

            logger.info(f"Bucket '{cls.BUCKET_NAME}' created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating bucket: {str(e)}")
            # If bucket creation fails, check if it exists (might have been created by another process)
            return cls.check_bucket_exists()

    @classmethod
    def get_mime_type(cls, filename: str) -> str:
        """
        Get MIME type from filename extension

        Args:
            filename: Filename with extension

        Returns:
            MIME type string
        """
        extension = Path(filename).suffix.lower()

        mime_types = {
            '.csv': 'text/csv',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.txt': 'text/plain',
            '.json': 'application/json',
        }

        return mime_types.get(extension, 'application/octet-stream')
