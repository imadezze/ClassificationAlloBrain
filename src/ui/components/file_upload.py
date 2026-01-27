"""File Upload Component with drag & drop support"""
import streamlit as st
from typing import Optional
import pandas as pd
from src.data_ingestion import FileParser


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

                    sheets = FileParser.parse_file(
                        file_bytes=file_bytes, file_name=uploaded_file.name
                    )

                    st.session_state.sheets = sheets
                    st.session_state.file_info = FileParser.get_file_info(sheets)

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
