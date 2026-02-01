"""Session Management Component - Load previous sessions"""
import streamlit as st
from typing import Optional
from datetime import datetime
from src.database.repositories import SessionRepository, UploadRepository
from src.storage import SupabaseStorage
from src.data_ingestion import FileParser
import logging

logger = logging.getLogger(__name__)


def render_session_loader() -> bool:
    """
    Render session loader UI

    Returns:
        True if a session was loaded
    """
    st.subheader("📂 Load Previous Session")

    # Get recent sessions
    try:
        recent_sessions = SessionRepository.list_recent_sessions(limit=10)

        if not recent_sessions:
            st.info("No previous sessions found")
            return False

        st.write(f"Found {len(recent_sessions)} recent sessions")

        # Display sessions in a table
        session_options = []
        for session in recent_sessions:
            # Format session info
            created = session.created_at.strftime("%Y-%m-%d %H:%M")
            status = session.status or "unknown"
            filename = session.original_filename or "Unnamed"

            # Get classification count if available
            from src.database.repositories import ClassificationRepository
            stats = ClassificationRepository.get_statistics(str(session.id))
            classification_count = stats.get("total_classified", 0)

            session_info = {
                "id": str(session.id),
                "filename": filename,
                "created": created,
                "status": status,
                "rows": session.total_rows or 0,
                "columns": session.total_columns or 0,
                "categories": session.num_categories or 0,
                "classifications": classification_count,
            }
            session_options.append(session_info)

        # Display as expandable items
        for i, session_info in enumerate(session_options):
            with st.expander(
                f"🗂️ {session_info['filename']} - {session_info['created']}"
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Status", session_info["status"])
                    st.metric("Rows", session_info["rows"])

                with col2:
                    st.metric("Columns", session_info["columns"])
                    st.metric("Categories", session_info["categories"])

                with col3:
                    st.metric("Classified", session_info["classifications"])

                # Load button
                if st.button(
                    "📥 Load This Session",
                    key=f"load_session_{i}",
                    use_container_width=True,
                ):
                    if load_session(session_info["id"]):
                        st.success("Session loaded successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to load session")

        return False

    except Exception as e:
        logger.error(f"Error loading sessions: {str(e)}")
        st.error(f"Error loading sessions: {str(e)}")
        return False


def load_session(session_id: str) -> bool:
    """
    Load a previous session into current session state

    Args:
        session_id: UUID of session to load

    Returns:
        True if successful
    """
    try:
        # Get session from database
        session = SessionRepository.get_session(session_id)
        if not session:
            st.error("Session not found")
            return False

        # Get upload info
        from src.database.repositories import UploadRepository
        upload = UploadRepository.get_by_session(session_id)

        if not upload or not upload.stored_filename:
            st.error("File not found in storage")
            return False

        # Download file from storage
        with st.spinner("Loading file from storage..."):
            # Extract session_id and filename from stored path
            file_path_parts = upload.stored_filename.split("/")
            if len(file_path_parts) != 2:
                st.error("Invalid file path format")
                return False

            storage_session_id, filename = file_path_parts

            file_bytes = SupabaseStorage.download_file(storage_session_id, filename)

        # Parse file
        with st.spinner("Parsing file..."):
            sheets = FileParser.parse_file(file_bytes=file_bytes, file_name=filename)

        # Restore session state
        st.session_state.db_session_id = session_id
        st.session_state.uploaded_file = None  # Don't have the actual file object
        st.session_state.file_name = session.original_filename
        st.session_state.file_size = upload.file_size_bytes
        st.session_state.sheets = sheets
        st.session_state.file_info = FileParser.get_file_info(sheets)
        st.session_state.file_hash = upload.file_hash

        # Restore selected sheet
        if session.selected_sheet:
            st.session_state.selected_sheet = session.selected_sheet

        # Restore selected column
        if session.selected_column:
            st.session_state.selected_column = session.selected_column

        # Restore categories
        if session.categories:
            st.session_state.discovered_categories = session.categories
            st.session_state.categories_finalized = True
            st.session_state.category_column = session.selected_column

        logger.info(f"Successfully loaded session {session_id}")
        return True

    except Exception as e:
        logger.error(f"Error loading session {session_id}: {str(e)}")
        st.error(f"Failed to load session: {str(e)}")
        return False


def render_quick_load_button() -> bool:
    """
    Render a quick button to load the most recent session

    Returns:
        True if a session was loaded
    """
    try:
        latest = SessionRepository.get_latest_session()

        if not latest:
            return False

        # Show in sidebar or main area
        created = latest.created_at.strftime("%Y-%m-%d %H:%M")
        filename = latest.original_filename or "Unnamed"

        st.info(f"💡 Last session: **{filename}** ({created})")

        if st.button("📥 Resume Last Session", use_container_width=True):
            if load_session(str(latest.id)):
                st.success("Session resumed!")
                st.rerun()
                return True
            else:
                st.error("Failed to resume session")

        return False

    except Exception as e:
        logger.error(f"Error in quick load: {str(e)}")
        return False
