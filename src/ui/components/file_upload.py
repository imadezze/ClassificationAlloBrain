"""File Upload Component with drag & drop support and database integration"""
import streamlit as st
from typing import Optional
import hashlib
import logging
from src.data_ingestion import FileParser, ColumnDetector
from src.database.repositories import SessionRepository, UploadRepository
from src.storage import SupabaseStorage

logger = logging.getLogger(__name__)


def render_file_upload() -> Optional[dict]:
    """
    Render file upload component with drag & drop

    Returns:
        Dictionary with uploaded file info or None
    """
    st.header("📁 File Upload")

    uploaded_file = st.file_uploader(
        "Upload your data file",
        type=["csv", "xlsx", "xls"],
        help="Drag and drop a CSV or Excel file here, or click to browse",
    )

    if uploaded_file is not None:
        # Store file in session state
        if "uploaded_file" not in st.session_state or st.session_state.uploaded_file != uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.file_name = uploaded_file.name
            st.session_state.file_size = uploaded_file.size

            # Parse file
            with st.spinner("Parsing file..."):
                try:
                    file_bytes = uploaded_file.read()
                    uploaded_file.seek(0)  # Reset file pointer

                    # Calculate file hash
                    file_hash = hashlib.md5(file_bytes).hexdigest()

                    # Determine file type
                    file_type = (
                        "excel"
                        if uploaded_file.name.endswith((".xlsx", ".xls"))
                        else "csv"
                    )

                    sheets = FileParser.parse_file(
                        file_bytes=file_bytes, file_name=uploaded_file.name
                    )

                    st.session_state.sheets = sheets
                    st.session_state.file_info = FileParser.get_file_info(sheets)
                    st.session_state.file_hash = file_hash

                    # Create or update database session
                    if "db_session_id" not in st.session_state:
                        # Create new session
                        db_session = SessionRepository.create_session(
                            original_filename=uploaded_file.name,
                            file_type=file_type,
                        )
                        st.session_state.db_session_id = str(db_session.id)
                        # Set 24-hour expiration
                        SessionRepository.set_expiration(db_session.id, hours=24)

                    # Get column metadata for the first sheet (or only sheet)
                    first_sheet_name = list(sheets.keys())[0]
                    first_df = sheets[first_sheet_name]
                    column_metadata = ColumnDetector.get_all_column_info(first_df)

                    # Update session with file metadata
                    SessionRepository.update_session(
                        st.session_state.db_session_id,
                        original_filename=uploaded_file.name,
                        file_type=file_type,
                        total_rows=st.session_state.file_info["total_rows"],
                        total_columns=st.session_state.file_info["total_columns"],
                        status="file_uploaded",
                    )

                    # Create Upload record
                    upload_data = {
                        "session_id": st.session_state.db_session_id,
                        "original_filename": uploaded_file.name,
                        "file_type": file_type,
                        "file_size_bytes": uploaded_file.size,
                        "file_hash": file_hash,
                        "row_count": st.session_state.file_info["total_rows"],
                        "column_count": st.session_state.file_info["total_columns"],
                        "column_metadata": column_metadata,
                    }

                    # Add Excel-specific metadata
                    if file_type == "excel":
                        upload_data["sheets"] = st.session_state.file_info["sheet_names"]

                    # Upload file to Supabase Storage
                    try:
                        storage_info = SupabaseStorage.upload_file(
                            file_bytes=file_bytes,
                            session_id=st.session_state.db_session_id,
                            filename=uploaded_file.name,
                            file_type=SupabaseStorage.get_mime_type(uploaded_file.name)
                        )
                        st.session_state.file_storage_url = storage_info["url"]
                        st.session_state.file_storage_path = storage_info["path"]

                        # Add storage info to upload_data
                        upload_data["stored_filename"] = storage_info["path"]

                    except Exception as e:
                        st.warning(f"⚠️ File uploaded but not saved to storage: {str(e)}")
                        logger.warning(f"Storage upload failed: {str(e)}")

                    # Check for duplicate upload
                    existing_upload = UploadRepository.find_by_hash(file_hash)
                    if not existing_upload:
                        upload = UploadRepository.create_upload(**upload_data)
                        st.session_state.db_upload_id = str(upload.id)

                        # Mark as processed
                        UploadRepository.update_upload_status(upload.id, "processed")
                    else:
                        st.session_state.db_upload_id = str(existing_upload.id)
                        st.info("💡 This file was previously uploaded")

                    # Reset downstream state
                    if "selected_sheet" in st.session_state:
                        del st.session_state.selected_sheet
                    if "selected_column" in st.session_state:
                        del st.session_state.selected_column
                    if "discovered_categories" in st.session_state:
                        del st.session_state.discovered_categories

                except Exception as e:
                    st.error(f"Error parsing file: {str(e)}")
                    return None

        # Display file info
        st.success(f"✓ File uploaded: {st.session_state.file_name}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{st.session_state.file_size / 1024:.1f} KB")
        with col2:
            st.metric("Sheets", st.session_state.file_info["num_sheets"])
        with col3:
            st.metric("Total Rows", st.session_state.file_info["total_rows"])

        return {
            "name": st.session_state.file_name,
            "size": st.session_state.file_size,
            "sheets": st.session_state.sheets,
            "info": st.session_state.file_info,
        }

    return None
