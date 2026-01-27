"""Data Preview Component with row limiting"""
import streamlit as st
import pandas as pd
from src.config import Config


def render_data_preview(df: pd.DataFrame, max_rows: int = None) -> None:
    """
    Render data preview with row limiting

    Args:
        df: DataFrame to preview
        max_rows: Maximum rows to display (defaults to Config.MAX_PREVIEW_ROWS)
    """
    if max_rows is None:
        max_rows = Config.MAX_PREVIEW_ROWS

    st.header("👀 Data Preview")

    total_rows = len(df)
    display_rows = min(total_rows, max_rows)

    # Info about preview
    if total_rows > max_rows:
        st.info(
            f"Showing first {display_rows} of {total_rows:,} rows "
            f"({(display_rows/total_rows)*100:.1f}% of data)"
        )
    else:
        st.info(f"Showing all {total_rows:,} rows")

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", f"{total_rows:,}")
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    with col4:
        null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        st.metric("Null Values", f"{null_percentage:.1f}%")

    # Data preview
    st.dataframe(
        df.head(display_rows),
        use_container_width=True,
        height=400,
    )

    # Column info expander
    with st.expander("📋 Column Information"):
        col_info = []
        for col in df.columns:
            col_info.append(
                {
                    "Column": col,
                    "Type": str(df[col].dtype),
                    "Non-Null": df[col].notna().sum(),
                    "Null": df[col].isna().sum(),
                    "Unique": df[col].nunique(),
                }
            )
        st.dataframe(pd.DataFrame(col_info), use_container_width=True)
