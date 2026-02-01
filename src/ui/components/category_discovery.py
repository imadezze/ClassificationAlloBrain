"""Category Discovery & Editor Component with database integration"""
import streamlit as st
import pandas as pd
from typing import Optional, List, Dict
from src.services import LLMService
from src.data_ingestion import DataSampler
from src.database.repositories import SessionRepository, CategoryHistoryRepository
from src.config import Config


def render_category_discovery(df: pd.DataFrame, column: str) -> Optional[List[Dict]]:
    """
    Render category discovery and editor interface

    Args:
        df: DataFrame with data
        column: Column name to analyze

    Returns:
        List of category definitions or None
    """
    st.header("🔍 Category Discovery")

    llm_service = LLMService()

    # Number of categories
    num_categories = st.slider(
        "Number of categories to discover",
        min_value=2,
        max_value=10,
        value=5,
        help="Suggest how many categories the LLM should identify",
    )

    # Discover categories button
    if st.button("🚀 Discover Categories", type="primary", width="stretch"):
        # Create placeholder for status updates
        status_placeholder = st.empty()

        # Sample data
        sample_values = DataSampler.get_column_sample(df, column, sample_size=50)

        # Progress callback for retry updates
        def update_progress(message):
            status_placeholder.warning(f"⚠️ {message}")

        with st.spinner("Analyzing data and discovering categories..."):
            # Call LLM to discover categories
            result = llm_service.discover_categories(
                column_name=column,
                sample_values=sample_values,
                num_categories=num_categories,
                max_retries=2,
                progress_callback=update_progress
            )

        # Clear status placeholder
        status_placeholder.empty()

        if result["success"]:
            st.session_state.discovered_categories = result["categories"]
            st.session_state.category_column = column

            # Save to database
            if "db_session_id" in st.session_state:
                SessionRepository.save_categories(
                    st.session_state.db_session_id,
                    categories=result["categories"],
                    num_categories=len(result["categories"])
                )

                # Save to category history
                attempts_text = f" on attempt {result['attempts']}" if result.get('attempts', 1) > 1 else ""
                CategoryHistoryRepository.create_history_entry(
                    session_id=st.session_state.db_session_id,
                    categories=result["categories"],
                    change_type="initial_discovery",
                    change_description=f"Discovered {len(result['categories'])} categories{attempts_text}"
                )

                # Update LLM settings
                SessionRepository.update_session(
                    st.session_state.db_session_id,
                    llm_model=Config.LLM_MODEL,
                    llm_temperature=Config.LLM_TEMPERATURE
                )

            # Show success message
            success_msg = f"✓ Discovered {len(result['categories'])} categories!"
            if result.get('attempts', 1) > 1:
                success_msg += f" (succeeded on attempt {result['attempts']})"

            if result.get("warning"):
                st.warning(result["warning"])

            st.success(success_msg)
        else:
            st.error(f"Failed to discover categories: {result.get('error', 'Unknown error')}")
            return None

    # Display and edit categories
    if "discovered_categories" in st.session_state:
        st.subheader("📝 Discovered Categories")

        categories = st.session_state.discovered_categories

        # Display categories in an editable format
        edited_categories = []

        for i, category in enumerate(categories):
            with st.expander(f"**{i+1}. {category['name']}**", expanded=True):
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Editable name
                    new_name = st.text_input(
                        "Category Name",
                        value=category["name"],
                        key=f"cat_name_{i}",
                    )

                    # Editable description
                    new_description = st.text_area(
                        "Description",
                        value=category["description"],
                        key=f"cat_desc_{i}",
                        height=100,
                    )

                    # Editable boundary
                    new_boundary = st.text_area(
                        "Boundary Definition",
                        value=category["boundary"],
                        key=f"cat_boundary_{i}",
                        height=80,
                    )

                with col2:
                    # Examples
                    st.write("**Examples:**")
                    for example in category.get("examples", []):
                        st.text(f"• {example}")

                # Add edited category
                edited_categories.append(
                    {
                        "name": new_name,
                        "description": new_description,
                        "boundary": new_boundary,
                        "examples": category.get("examples", []),
                    }
                )

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Save Categories", width="stretch"):
                st.session_state.discovered_categories = edited_categories
                st.session_state.categories_finalized = True

                # Update database with edited categories
                if "db_session_id" in st.session_state:
                    SessionRepository.save_categories(
                        st.session_state.db_session_id,
                        categories=edited_categories,
                        num_categories=len(edited_categories)
                    )

                    # Save to category history
                    CategoryHistoryRepository.create_history_entry(
                        session_id=st.session_state.db_session_id,
                        categories=edited_categories,
                        change_type="user_edit",
                        change_description="Manually edited category definitions"
                    )

                st.success("Categories saved!")
                st.rerun()

        with col2:
            if st.button("🔄 Refine with Feedback", width="stretch"):
                st.session_state.show_refinement = True

        with col3:
            if st.button("🗑️ Clear Categories", width="stretch"):
                del st.session_state.discovered_categories
                if "categories_finalized" in st.session_state:
                    del st.session_state.categories_finalized
                st.rerun()

        # Refinement interface
        if st.session_state.get("show_refinement", False):
            st.divider()
            st.subheader("🔧 Refine Categories")

            feedback = st.text_area(
                "Provide feedback on how to improve the categories",
                placeholder="E.g., 'Merge Customer Support and Technical Support into one category' or 'Add a category for Billing issues'",
                height=100,
            )

            if st.button("Apply Refinements", type="primary"):
                if feedback:
                    with st.spinner("Refining categories..."):
                        sample_values = DataSampler.get_column_sample(df, column, sample_size=30)

                        result = llm_service.refine_categories(
                            categories=st.session_state.discovered_categories,
                            feedback=feedback,
                            sample_values=sample_values,
                        )

                        if result["success"]:
                            st.session_state.discovered_categories = result["categories"]
                            st.session_state.show_refinement = False

                            # Save refinement to database
                            if "db_session_id" in st.session_state:
                                # Update session with refined categories
                                SessionRepository.save_categories(
                                    st.session_state.db_session_id,
                                    categories=result["categories"],
                                    num_categories=len(result["categories"])
                                )

                                # Save to category history with feedback
                                CategoryHistoryRepository.create_history_entry(
                                    session_id=st.session_state.db_session_id,
                                    categories=result["categories"],
                                    change_type="llm_refinement",
                                    user_feedback=feedback,
                                    change_description="LLM-refined categories based on user feedback"
                                )

                            st.success("Categories refined!")
                            st.rerun()
                        else:
                            st.error(f"Refinement failed: {result.get('error')}")
                else:
                    st.warning("Please provide feedback first")

        return st.session_state.discovered_categories

    return None
