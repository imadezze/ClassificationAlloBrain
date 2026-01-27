"""Sheet Selector Component for multi-sheet Excel files"""
import streamlit as st
from typing import Optional
import pandas as pd


def render_sheet_selector(sheets: dict) -> Optional[str]:
    """
    Render sheet selector for multi-sheet files

    Args:
        sheets: Dictionary of sheet names to DataFrames

    Returns:
        Selected sheet name or None
    """
    if not sheets:
        return None

    st.header("📊 Sheet Selection")

    # If only one sheet, auto-select it
    if len(sheets) == 1:
        selected_sheet = list(sheets.keys())[0]
        st.info(f"Auto-selected sheet: **{selected_sheet}**")
        st.session_state.selected_sheet = selected_sheet
        return selected_sheet

    # Multiple sheets - let user choose
    sheet_names = list(sheets.keys())

    # Create columns to show sheet info
    st.write("**Available Sheets:**")

    for sheet_name in sheet_names:
        df = sheets[sheet_name]
        with st.expander(f"📄 {sheet_name} ({len(df)} rows, {len(df.columns)} columns)"):
            st.dataframe(df.head(3), use_container_width=True)

    # Sheet selector
    selected_sheet = st.selectbox(
        "Select a sheet to work with",
        options=sheet_names,
        index=0,
        key="sheet_selector",
    )

    if selected_sheet:
        st.session_state.selected_sheet = selected_sheet
        return selected_sheet

    return None
