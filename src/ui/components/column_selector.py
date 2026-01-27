"""Column Selector Component with auto-detection"""
import streamlit as st
import pandas as pd
from typing import Optional
from src.data_ingestion import ColumnDetector


def render_column_selector(df: pd.DataFrame) -> Optional[str]:
    """
    Render column selector with auto-detection of text columns

    Args:
        df: DataFrame to analyze

    Returns:
        Selected column name or None
    """
    st.header("🎯 Column Selection")

    # Detect text columns
    with st.spinner("Analyzing columns..."):
        text_columns = ColumnDetector.detect_text_columns(df)
        suggested_column = ColumnDetector.suggest_classification_target(df)

    if not text_columns:
        st.error("No text columns detected in the data. Please upload a file with text data.")
        return None

    # Display detected text columns
    st.success(f"Found {len(text_columns)} text column(s)")

    # Show column statistics
    with st.expander("📊 Text Column Details"):
        for col in text_columns:
            stats = ColumnDetector.get_column_stats(df, col)
            st.markdown(f"**{col}**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Non-null", stats["non_null_rows"])
            with col2:
                st.metric("Unique", stats["unique_values"])
            with col3:
                st.metric("Avg Length", f"{stats['avg_text_length']:.0f}")
            with col4:
                st.metric("Null %", f"{stats['null_percentage']:.1f}%")

            # Show samples
            if stats.get("sample_values"):
                with st.expander(f"Sample values from {col}"):
                    for val in stats["sample_values"]:
                        st.text(f"• {val}")
            st.divider()

    # Column selector
    default_index = 0
    if suggested_column and suggested_column in text_columns:
        default_index = text_columns.index(suggested_column)
        st.info(f"💡 Suggested column: **{suggested_column}** (based on content analysis)")

    selected_column = st.selectbox(
        "Select column to classify",
        options=text_columns,
        index=default_index,
        key="column_selector",
        help="Choose the text column you want to classify into categories",
    )

    if selected_column:
        # Validate column
        validation = ColumnDetector.validate_column_for_classification(df, selected_column)

        if not validation["valid"]:
            st.error(f"⚠️ {validation['reason']}")
            return None

        st.success(f"✓ Selected column: **{selected_column}**")
        st.session_state.selected_column = selected_column

        # Show sample values from selected column
        with st.expander("Preview selected column values"):
            sample_df = df[[selected_column]].dropna().head(10)
            st.dataframe(sample_df, use_container_width=True)

        return selected_column

    return None
