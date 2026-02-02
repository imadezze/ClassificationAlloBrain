"""Evaluation Interface - Comprehensive classification evaluation UI"""
import streamlit as st
import pandas as pd
from typing import List, Dict
import time
from src.services.evaluation_service import EvaluationService
import logging

logger = logging.getLogger(__name__)


def render_evaluation_interface(
    df: pd.DataFrame,
    column: str,
    categories: List[Dict],
    classification_results: List[Dict]
) -> None:
    """
    Render evaluation interface with multiple evaluation methods

    Args:
        df: DataFrame with data
        column: Column being classified
        categories: List of category definitions
        classification_results: Results from classification
    """
    st.header("📊 Evaluation Framework")

    st.markdown("""
    Evaluate classification quality without golden labels using multiple methods:
    - **Self-Consistency**: Test robustness across temperatures
    - **Synthetic Testing**: Generate and classify test examples
    - **LLM-as-Judge**: Use stronger models to evaluate decisions
    - **Cross-Model Validation**: Multi-model consensus
    """)

    # Initialize evaluation service
    eval_service = EvaluationService()

    # Tabs for different evaluation methods
    tabs = st.tabs([
        "🔄 Self-Consistency",
        "🧪 Synthetic Testing",
        "⚖️ LLM-as-Judge",
        "📈 Full Report"
    ])

    # Tab 1: Self-Consistency Evaluation
    with tabs[0]:
        render_self_consistency_tab(eval_service, df, column, categories, classification_results)

    # Tab 2: Synthetic Testing
    with tabs[1]:
        render_synthetic_testing_tab(eval_service, df, column, categories)

    # Tab 3: LLM-as-Judge
    with tabs[2]:
        render_llm_judge_tab(eval_service, df, column, categories, classification_results)

    # Tab 4: Full Report
    with tabs[3]:
        render_full_report_tab(eval_service, df, column, categories, classification_results)


def render_self_consistency_tab(
    eval_service: EvaluationService,
    df: pd.DataFrame,
    column: str,
    categories: List[Dict],
    classification_results: List[Dict]
):
    """Render self-consistency evaluation tab"""
    st.subheader("🔄 Self-Consistency Evaluation")

    st.markdown("""
    Test classification robustness by classifying the same input multiple times
    with different temperatures. High agreement indicates confident, reliable predictions.
    """)

    # Sample selection
    col1, col2 = st.columns([2, 1])

    with col1:
        if classification_results:
            sample_options = [f"{r['value'][:50]}..." for r in classification_results[:10]]
            selected_idx = st.selectbox(
                "Select text to evaluate",
                range(len(sample_options)),
                format_func=lambda i: sample_options[i]
            )
        else:
            st.warning("No classification results available. Please classify data first.")
            return

    with col2:
        num_runs = st.number_input("Runs per temperature", min_value=2, max_value=5, value=3)

    if st.button("🔄 Run Consistency Test", type="primary", use_container_width=True):
        selected_text = classification_results[selected_idx]["value"]

        with st.spinner("Running consistency evaluation..."):
            result = eval_service.self_consistency_evaluation(
                text=selected_text,
                categories=categories,
                column_name=column,
                temperatures=[0.1, 0.5, 0.9],
                num_runs=num_runs
            )

        if result["success"]:
            # Display results
            st.success(f"✓ Completed {result['total_runs']} runs")

            # Metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Agreement Rate",
                    f"{result['agreement_rate']:.0%}",
                    help="How often the same prediction was made"
                )

            with col2:
                st.metric(
                    "Consensus",
                    result['agreement_count'],
                    help="Number of times most common prediction appeared"
                )

            with col3:
                confidence_emoji = {
                    "high": "🟢",
                    "medium": "🟡",
                    "low": "🔴"
                }
                st.metric(
                    "Confidence",
                    f"{confidence_emoji[result['confidence_level']]} {result['confidence_level'].title()}"
                )

            # Prediction distribution
            st.subheader("Prediction Distribution")
            pred_df = pd.DataFrame(list(result['predictions'].items()), columns=["Category", "Count"])
            st.bar_chart(pred_df.set_index("Category"))

            # Recommendation
            st.info(f"💡 **Recommendation:** {result['recommendation']}")

            # Detailed results
            with st.expander("📋 Detailed Results"):
                st.dataframe(pd.DataFrame(result['detailed_results']), use_container_width=True)

        else:
            st.error(f"Error: {result.get('error', 'Unknown error')}")


def render_synthetic_testing_tab(
    eval_service: EvaluationService,
    df: pd.DataFrame,
    column: str,
    categories: List[Dict]
):
    """Render synthetic testing tab"""
    st.subheader("🧪 Synthetic Testing")

    st.markdown("""
    Generate synthetic examples for each category and test if they classify correctly.
    High accuracy indicates the classifier understands category boundaries.
    """)

    # Select category to test
    category_names = [cat["name"] for cat in categories]
    selected_category_name = st.selectbox("Select category to test", category_names)

    selected_category = next(cat for cat in categories if cat["name"] == selected_category_name)

    col1, col2 = st.columns(2)

    with col1:
        num_examples = st.number_input("Number of examples", min_value=3, max_value=10, value=5)

    with col2:
        test_all = st.checkbox("Test all categories", value=False)

    if st.button("🧪 Generate & Test Examples", type="primary", use_container_width=True):
        categories_to_test = categories if test_all else [selected_category]

        progress_bar = st.progress(0)
        all_results = []

        for i, cat in enumerate(categories_to_test):
            st.write(f"**Testing category:** {cat['name']}")

            # Generate examples
            with st.spinner(f"Generating examples for {cat['name']}..."):
                gen_result = eval_service.generate_contrastive_examples(
                    category=cat,
                    num_examples=num_examples
                )

            if gen_result["success"]:
                # Classify generated examples
                with st.spinner(f"Classifying examples for {cat['name']}..."):
                    class_result = eval_service.classify_generated_examples(
                        generated_examples=gen_result["examples"],
                        categories=categories,
                        column_name=column,
                        expected_category=cat["name"]
                    )

                all_results.append({
                    "category": cat["name"],
                    "accuracy": class_result["accuracy"],
                    "correct": class_result["correct"],
                    "total": class_result["total_examples"],
                    "quality": class_result["quality_assessment"],
                    "details": class_result["results"]
                })

                # Show immediate results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Accuracy", f"{class_result['accuracy']:.1f}%")
                with col2:
                    st.metric("Correct", f"{class_result['correct']}/{class_result['total_examples']}")
                with col3:
                    quality_color = {
                        "Excellent": "🟢",
                        "Moderate": "🟡",
                        "Poor": "🔴"
                    }
                    quality_key = class_result["quality_assessment"].split("-")[0].strip()
                    st.metric("Quality", f"{quality_color.get(quality_key, '⚪')} {quality_key}")

                # Detailed results
                with st.expander(f"📋 Details for {cat['name']}"):
                    st.dataframe(pd.DataFrame(class_result["results"]), use_container_width=True)

            progress_bar.progress((i + 1) / len(categories_to_test))

        # Summary if testing all categories
        if test_all and all_results:
            st.divider()
            st.subheader("📊 Overall Summary")

            summary_df = pd.DataFrame([
                {
                    "Category": r["category"],
                    "Accuracy (%)": f"{r['accuracy']:.1f}",
                    "Correct/Total": f"{r['correct']}/{r['total']}",
                    "Quality": r["quality"]
                }
                for r in all_results
            ])

            st.dataframe(summary_df, use_container_width=True)

            avg_accuracy = sum(r["accuracy"] for r in all_results) / len(all_results)
            st.metric("Average Accuracy", f"{avg_accuracy:.1f}%")


def render_llm_judge_tab(
    eval_service: EvaluationService,
    df: pd.DataFrame,
    column: str,
    categories: List[Dict],
    classification_results: List[Dict]
):
    """Render LLM-as-Judge evaluation tab"""
    st.subheader("⚖️ LLM-as-Judge Evaluation")

    st.markdown("""
    Use stronger models to evaluate classification decisions.
    Cross-model validation uses 2 judges: Claude Opus 4.5 (Bedrock) and GPT-5.2.
    Provides independent judgment from the most capable models.
    """)

    # Judge model selection
    col1, col2 = st.columns([2, 1])

    with col1:
        use_cross_model = st.checkbox(
            "Use cross-model validation (2 judges)",
            value=True,
            help="Use Claude Opus 4.5 (Bedrock) and GPT-5.2 for consensus"
        )

    with col2:
        sample_size = st.number_input("Sample size", min_value=1, max_value=20, value=5)

    if st.button("⚖️ Run Judge Evaluation", type="primary", use_container_width=True):
        # Sample classifications to evaluate
        import random
        sample = random.sample(classification_results, min(sample_size, len(classification_results)))

        progress_bar = st.progress(0)
        judge_results = []

        for i, item in enumerate(sample):
            with st.spinner(f"Evaluating {i+1}/{len(sample)}..."):
                result = eval_service.llm_as_judge_evaluation(
                    text=item["value"],
                    predicted_category=item["predicted_category"],
                    categories=categories,
                    column_name=column,
                    confidence=item.get("confidence"),
                    use_cross_model=use_cross_model
                )

                if result["success"]:
                    judge_results.append(result)

            progress_bar.progress((i + 1) / len(sample))

        # Display aggregated results
        if judge_results:
            st.success(f"✓ Evaluated {len(judge_results)} classifications")

            # Overall metrics
            total_agreements = sum(r["agreement_count"] for r in judge_results)
            total_possible = sum(r["total_judges"] for r in judge_results)
            overall_agreement_rate = total_agreements / total_possible

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Overall Agreement", f"{overall_agreement_rate:.0%}")

            with col2:
                confirmed = sum(1 for r in judge_results if "confirmed" in r["final_verdict"].lower())
                st.metric("Confirmed Correct", f"{confirmed}/{len(judge_results)}")

            with col3:
                questionable = sum(1 for r in judge_results if "questionable" in r["final_verdict"].lower())
                st.metric("Needs Review", questionable)

            # Detailed results
            st.subheader("📋 Judge Evaluations")

            for i, result in enumerate(judge_results):
                with st.expander(f"Item {i+1}: {result['text'][:60]}..."):
                    st.write(f"**Predicted:** {result['predicted_category']}")
                    st.write(f"**Verdict:** {result['final_verdict']}")
                    st.write(f"**Consensus:** {result['consensus']}")

                    # Judge details
                    for judge in result["judge_results"]:
                        st.markdown(f"**{judge['judge_name']}:**")
                        st.json(judge)


def render_full_report_tab(
    eval_service: EvaluationService,
    df: pd.DataFrame,
    column: str,
    categories: List[Dict],
    classification_results: List[Dict]
):
    """Render full evaluation report"""
    st.subheader("📈 Full Evaluation Report")

    st.markdown("""
    Comprehensive evaluation combining all methods for a complete quality assessment.
    """)

    if st.button("📊 Generate Full Report", type="primary", use_container_width=True):
        st.info("🚧 Full report generation coming soon! Run individual evaluations in the tabs above.")

        # Placeholder for future comprehensive report
        st.markdown("""
        **Planned features:**
        - Automated sampling strategy
        - Multi-method evaluation pipeline
        - Confidence calibration curves
        - Category-wise performance breakdown
        - Trend analysis over time
        - Automated improvement suggestions
        """)
