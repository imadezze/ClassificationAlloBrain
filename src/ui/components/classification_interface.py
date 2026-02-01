"""Classification Interface Component with database integration"""
import streamlit as st
import pandas as pd
from typing import List, Dict
import time
import logging
from src.services import LLMService
from src.data_ingestion import DataSampler
from src.database.repositories import SessionRepository, ClassificationRepository
from src.config import Config

logger = logging.getLogger(__name__)


def retry_classification_with_feedback(
    df: pd.DataFrame,
    column: str,
    categories: List[Dict],
    selected_indices: List[int],
    feedback: str,
    results: List[Dict]
):
    """
    Retry classification for selected rows with user feedback

    Args:
        df: DataFrame with data
        column: Column name
        categories: List of categories
        selected_indices: Indices of rows to reclassify
        feedback: User feedback to add to prompt
        results: Original results list to update
    """
    llm_service = LLMService()

    # Reclassify selected rows
    for idx in selected_indices:
        value = results[idx]["value"]

        # Classify with feedback
        result = llm_service.classify_value_with_feedback(
            value=value,
            categories=categories,
            column_name=column,
            feedback=feedback
        )

        # Update results
        if result["success"]:
            results[idx]["predicted_category"] = result["predicted_category"]
            results[idx]["confidence"] = result.get("confidence", "medium")

            # Update database
            if "db_session_id" in st.session_state:
                try:
                    # Find and update the classification record
                    from src.database.connection import DatabaseConnection
                    from src.database.models import Classification

                    with DatabaseConnection.get_session() as db:
                        classification = (
                            db.query(Classification)
                            .filter(
                                Classification.session_id == st.session_state.db_session_id,
                                Classification.input_text == value
                            )
                            .first()
                        )

                        if classification:
                            classification.predicted_category = result["predicted_category"]
                            classification.confidence = result.get("confidence", "medium")
                            db.commit()
                except Exception as e:
                    logger.warning(f"Failed to update database: {e}")


def render_classification_interface(
    df: pd.DataFrame, column: str, categories: List[Dict]
) -> None:
    """
    Render classification interface

    Args:
        df: DataFrame with data
        column: Column to classify
        categories: List of category definitions
    """
    st.header("🎯 Classification")

    if not categories:
        st.warning("Please discover categories first")
        return

    llm_service = LLMService()

    # Classification options
    col1, col2 = st.columns(2)

    with col1:
        classification_mode = st.radio(
            "Classification Mode",
            ["Sample (Quick Test)", "Full Dataset"],
            help="Sample mode classifies a subset for quick testing. Full mode classifies all data.",
        )

    with col2:
        if classification_mode == "Sample (Quick Test)":
            sample_size = st.number_input(
                "Sample Size",
                min_value=5,
                max_value=100,
                value=20,
                step=5,
            )

    # Classify button
    if st.button("🚀 Start Classification", type="primary", width="stretch"):
        # Determine data to classify
        if classification_mode == "Sample (Quick Test)":
            data_to_classify = DataSampler.random_sample(df, sample_size)
            st.info(f"Classifying {len(data_to_classify)} sampled rows...")
            mode = "sample"
        else:
            data_to_classify = df
            st.info(f"Classifying all {len(data_to_classify)} rows...")
            mode = "full_dataset"

        # Update session status
        if "db_session_id" in st.session_state:
            SessionRepository.update_session(
                st.session_state.db_session_id,
                status="classification_in_progress",
                classification_mode=mode,
                classification_sample_size=len(data_to_classify) if mode == "sample" else None
            )

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        values_to_classify = data_to_classify[column].dropna().tolist()
        results = []
        classifications_to_save = []

        for i, value in enumerate(values_to_classify):
            # Update progress
            progress = (i + 1) / len(values_to_classify)
            progress_bar.progress(progress)
            status_text.text(f"Classifying {i+1}/{len(values_to_classify)}...")

            # Track execution time
            start_time = time.time()

            # Classify
            result = llm_service.classify_value(value, categories, column)

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            results.append(result)

            # Prepare for database save
            if "db_session_id" in st.session_state:
                classifications_to_save.append({
                    "session_id": st.session_state.db_session_id,
                    "input_text": value,
                    "row_index": i,
                    "predicted_category": result.get("predicted_category", ""),
                    "confidence": result.get("confidence"),
                    "llm_model": Config.LLM_MODEL,
                    "llm_temperature": Config.LLM_TEMPERATURE,
                    "execution_time_ms": execution_time_ms,
                    "success": result.get("success", False),
                    "error_message": result.get("error") if not result.get("success", False) else None
                })

        # Save classifications to database
        if "db_session_id" in st.session_state and classifications_to_save:
            ClassificationRepository.bulk_create_classifications(classifications_to_save)

            # Update session status to completed
            SessionRepository.update_session(
                st.session_state.db_session_id,
                status="completed"
            )

        # Store results
        st.session_state.classification_results = results
        st.session_state.classification_df = data_to_classify
        st.success(f"✓ Classified {len(results)} values!")

        progress_bar.empty()
        status_text.empty()

    # Display results
    if "classification_results" in st.session_state:
        st.divider()
        st.subheader("📊 Classification Results")

        results = st.session_state.classification_results

        # Get statistics from database if available
        if "db_session_id" in st.session_state:
            db_stats = ClassificationRepository.get_statistics(st.session_state.db_session_id)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Classified", db_stats["total"])
            with col2:
                st.metric("Successful", db_stats["successful"])
            with col3:
                st.metric("Success Rate", f"{db_stats['success_rate']:.1f}%")
            with col4:
                st.metric("Avg Time", f"{db_stats['avg_execution_time_ms']:.0f}ms")
        else:
            # Fallback to session state statistics
            successful = sum(1 for r in results if r["success"])
            failed = len(results) - successful

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Classified", len(results))
            with col2:
                st.metric("Successful", successful)
            with col3:
                st.metric("Failed", failed)

        # Category distribution
        st.subheader("📈 Category Distribution")

        category_counts = {}
        for result in results:
            if result["success"]:
                cat = result["predicted_category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1

        # Display as bar chart
        if category_counts:
            chart_df = pd.DataFrame(
                list(category_counts.items()), columns=["Category", "Count"]
            )
            st.bar_chart(chart_df.set_index("Category"))

        # Detailed results table with retry functionality
        with st.expander("🔍 Detailed Results"):
            results_df = pd.DataFrame(results)

            # Add row selection for retry
            st.subheader("Select rows to reclassify")

            # Create editable dataframe with selection
            edited_df = results_df.copy()
            edited_df.insert(0, "Select", False)

            # Display with checkboxes
            col1, col2 = st.columns([3, 1])

            with col1:
                # Show data editor for selection
                selected_results = st.data_editor(
                    edited_df,
                    disabled=["value", "predicted_category", "confidence", "success"],
                    hide_index=True,
                    use_container_width=True,
                    key="results_selector"
                )

            with col2:
                # Count selected rows
                selected_count = selected_results["Select"].sum()
                st.metric("Selected", selected_count)

                # Feedback text area
                retry_feedback = st.text_area(
                    "Feedback for retry",
                    placeholder="E.g., 'Be more specific about technical issues' or 'Consider the context of customer service'",
                    height=100,
                    help="This feedback will be added to the classification prompt"
                )

                # Retry button
                if st.button(
                    f"🔄 Retry {selected_count} Selected",
                    disabled=selected_count == 0,
                    type="primary",
                    use_container_width=True
                ):
                    if selected_count > 0:
                        # Get indices of selected rows
                        selected_indices = selected_results[selected_results["Select"]].index.tolist()

                        with st.spinner(f"Reclassifying {selected_count} rows..."):
                            retry_classification_with_feedback(
                                df=st.session_state.classification_df,
                                column=column,
                                categories=categories,
                                selected_indices=selected_indices,
                                feedback=retry_feedback,
                                results=results
                            )

                        st.success(f"✓ Reclassified {selected_count} rows!")
                        st.rerun()

        # Download results
        if st.button("💾 Download Results as CSV", width="stretch"):
            # Create export DataFrame
            export_df = st.session_state.classification_df.copy()
            export_df[f"{column}_category"] = [
                r["predicted_category"] if r["success"] else "ERROR"
                for r in results
            ]

            csv = export_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="classification_results.csv",
                mime="text/csv",
            )
