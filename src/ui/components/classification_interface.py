"""Classification Interface Component"""
import streamlit as st
import pandas as pd
from typing import List, Dict
from src.services import LLMService
from src.data_ingestion import DataSampler


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
    if st.button("🚀 Start Classification", type="primary", use_container_width=True):
        # Determine data to classify
        if classification_mode == "Sample (Quick Test)":
            data_to_classify = DataSampler.random_sample(df, sample_size)
            st.info(f"Classifying {len(data_to_classify)} sampled rows...")
        else:
            data_to_classify = df
            st.info(f"Classifying all {len(data_to_classify)} rows...")

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        values_to_classify = data_to_classify[column].dropna().tolist()
        results = []

        for i, value in enumerate(values_to_classify):
            # Update progress
            progress = (i + 1) / len(values_to_classify)
            progress_bar.progress(progress)
            status_text.text(f"Classifying {i+1}/{len(values_to_classify)}...")

            # Classify
            result = llm_service.classify_value(value, categories, column)
            results.append(result)

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

        # Summary statistics
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

        # Detailed results table
        with st.expander("🔍 Detailed Results"):
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)

        # Download results
        if st.button("💾 Download Results as CSV", use_container_width=True):
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
