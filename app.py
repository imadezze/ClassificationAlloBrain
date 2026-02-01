"""
Semantic Classifier - Streamlit Application
Main entry point for the data ingestion and classification system
"""
import streamlit as st
from src.config import Config
from src.ui.components import (
    render_file_upload,
    render_sheet_selector,
    render_data_preview,
    render_column_selector,
    render_category_discovery,
    render_classification_interface,
    render_session_loader,
    render_quick_load_button,
)


def init_session_state():
    """Initialize session state variables"""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_step = 1


def check_config():
    """Check if configuration is valid"""
    if not Config.validate():
        st.error(
            """
            ⚠️ **Configuration Error**

            OpenAI API key is not configured. Please:
            1. Copy `.env.example` to `.env`
            2. Add your OpenAI API key to `.env`
            3. Restart the application
            """
        )
        st.stop()


def render_sidebar():
    """Render sidebar with navigation and info"""
    with st.sidebar:
        st.title("🧠 Semantic Classifier")
        st.markdown("---")

        st.subheader("📋 Workflow Steps")

        steps = [
            "1️⃣ Upload File",
            "2️⃣ Select Sheet",
            "3️⃣ Preview Data",
            "4️⃣ Select Column",
            "5️⃣ Discover Categories",
            "6️⃣ Classify Data",
        ]

        for step in steps:
            st.markdown(step)

        st.markdown("---")

        st.subheader("ℹ️ About")
        st.markdown(
            """
            This tool helps you:
            - Upload CSV/Excel files
            - Auto-detect text columns
            - Discover categories with AI
            - Classify data into categories
            """
        )

        st.markdown("---")

        st.subheader("⚙️ Configuration")
        st.code(f"Model: {Config.LLM_MODEL}")
        st.code(f"Temperature: {Config.LLM_TEMPERATURE}")
        st.code(f"Max Preview: {Config.MAX_PREVIEW_ROWS} rows")

        st.markdown("---")

        # Session Management
        st.subheader("💾 Sessions")

        # Quick load button for last session
        render_quick_load_button()

        st.markdown("---")

        # Reset button
        if st.button("🔄 Reset All", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def main():
    """Main application function"""
    # Page config
    st.set_page_config(
        page_title="Semantic Classifier",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize
    init_session_state()
    check_config()

    # Render sidebar
    render_sidebar()

    # Main content
    st.title("🧠 Semantic Classifier")
    st.markdown("### AI-Powered Data Classification System")
    st.markdown("---")

    # Step 1: File Upload
    file_data = render_file_upload()

    if not file_data:
        st.info("👆 Upload a file to get started")
        return

    st.markdown("---")

    # Step 2: Sheet Selection
    sheets = file_data["sheets"]
    selected_sheet = render_sheet_selector(sheets)

    if not selected_sheet:
        return

    st.markdown("---")

    # Get the DataFrame for the selected sheet
    df = sheets[selected_sheet]

    # Step 3: Data Preview
    render_data_preview(df)

    st.markdown("---")

    # Step 4: Column Selection
    selected_column = render_column_selector(df)

    if not selected_column:
        return

    st.markdown("---")

    # Step 5: Category Discovery
    categories = render_category_discovery(df, selected_column)

    if not categories:
        st.info("👆 Discover categories to proceed to classification")
        return

    if not st.session_state.get("categories_finalized", False):
        st.info("👆 Save categories to proceed to classification")
        return

    st.markdown("---")

    # Step 6: Classification
    render_classification_interface(df, selected_column, categories)


if __name__ == "__main__":
    main()
