"""Few-Shot Examples Component - Allow users to provide classification examples"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
import logging
from src.database.repositories import FewShotExampleRepository

logger = logging.getLogger(__name__)


def render_few_shot_examples(categories: List[Dict], column_name: str) -> Optional[List[Dict]]:
    """
    Render UI for users to provide few-shot examples

    Args:
        categories: List of category definitions
        column_name: Name of the column being classified

    Returns:
        List of example dictionaries or None
    """
    st.subheader("📚 Few-Shot Examples (Optional)")
    st.caption("Provide examples to guide the AI's classification. This can significantly improve accuracy.")

    # Load examples from database if we have a session
    if "few_shot_examples_loaded" not in st.session_state:
        if "db_session_id" in st.session_state:
            try:
                # Load examples from database
                db_examples = FewShotExampleRepository.get_session_examples(
                    st.session_state.db_session_id,
                    column_name=column_name
                )

                # Convert to session state format
                st.session_state.few_shot_examples = FewShotExampleRepository.examples_to_dict(db_examples)
                st.session_state.few_shot_examples_loaded = True

                if db_examples:
                    logger.info(f"Loaded {len(db_examples)} few-shot examples from database")
            except Exception as e:
                logger.warning(f"Could not load examples from database: {e}")
                st.session_state.few_shot_examples = []
                st.session_state.few_shot_examples_loaded = True
        else:
            # No session yet, start with empty
            st.session_state.few_shot_examples = []
            st.session_state.few_shot_examples_loaded = True

    # Show info
    with st.expander("ℹ️ How Few-Shot Learning Works"):
        st.markdown("""
        **Few-shot learning** improves classification by showing the AI examples of how you want values classified.

        **Benefits:**
        - 🎯 More accurate classifications
        - 📈 Better handling of edge cases
        - 🔧 Fine-tuned to your specific use case

        **Best Practices:**
        - Provide 2-5 examples per category
        - Choose diverse, representative examples
        - Include edge cases or ambiguous examples
        """)

    # Example entry method
    entry_method = st.radio(
        "How would you like to add examples?",
        ["➕ Add Manually", "📋 Upload CSV"],
        horizontal=True
    )

    if entry_method == "➕ Add Manually":
        # Manual entry form
        with st.form("add_example_form"):
            st.write("**Add New Example**")

            col1, col2 = st.columns([2, 1])

            with col1:
                example_text = st.text_input(
                    f"Example {column_name} value",
                    placeholder="E.g., 'I can't log into my account'",
                    help="Enter a text value to classify"
                )

            with col2:
                category_names = [cat["name"] for cat in categories]
                example_category = st.selectbox(
                    "Correct Category",
                    options=category_names,
                    help="Select the correct category for this example"
                )

            # Optional reasoning
            reasoning = st.text_area(
                "Reasoning (optional)",
                placeholder="Why does this belong in this category?",
                help="Explain why this example belongs in the selected category"
            )

            # Submit button
            submitted = st.form_submit_button("➕ Add Example", type="primary")

            if submitted and example_text:
                # Add to examples
                new_example = {
                    "text": example_text,
                    "category": example_category,
                    "reasoning": reasoning if reasoning else None
                }

                st.session_state.few_shot_examples.append(new_example)

                # Save to database if we have a session
                if "db_session_id" in st.session_state:
                    try:
                        FewShotExampleRepository.create_example(
                            example_text=example_text,
                            category=example_category,
                            session_id=st.session_state.db_session_id,
                            reasoning=reasoning if reasoning else None,
                            column_name=column_name,
                            is_global=False,
                            display_order=len(st.session_state.few_shot_examples) - 1
                        )
                        logger.info(f"Saved example to database: {example_text}")
                    except Exception as e:
                        logger.warning(f"Could not save example to database: {e}")

                st.success(f"✓ Added example: '{example_text}' → {example_category}")
                st.rerun()

    else:
        # CSV upload
        st.write("**Upload Examples CSV**")
        st.caption("CSV should have columns: 'text' and 'category' (optional: 'reasoning')")

        uploaded_csv = st.file_uploader(
            "Upload CSV file",
            type=["csv"],
            help="Upload a CSV with example classifications"
        )

        if uploaded_csv:
            try:
                examples_df = pd.read_csv(uploaded_csv)

                # Validate columns
                if "text" not in examples_df.columns or "category" not in examples_df.columns:
                    st.error("CSV must have 'text' and 'category' columns")
                else:
                    # Show preview
                    st.write(f"**Preview** ({len(examples_df)} examples)")
                    st.dataframe(examples_df.head(), use_container_width=True)

                    if st.button("✓ Import Examples", type="primary"):
                        # Convert to examples format
                        imported_count = 0
                        for _, row in examples_df.iterrows():
                            new_example = {
                                "text": str(row["text"]),
                                "category": str(row["category"]),
                                "reasoning": str(row.get("reasoning", "")) if "reasoning" in row else None
                            }
                            st.session_state.few_shot_examples.append(new_example)

                            # Save to database if we have a session
                            if "db_session_id" in st.session_state:
                                try:
                                    FewShotExampleRepository.create_example(
                                        example_text=str(row["text"]),
                                        category=str(row["category"]),
                                        session_id=st.session_state.db_session_id,
                                        reasoning=str(row.get("reasoning", "")) if "reasoning" in row else None,
                                        column_name=column_name,
                                        is_global=False,
                                        display_order=len(st.session_state.few_shot_examples) - 1
                                    )
                                    imported_count += 1
                                except Exception as e:
                                    logger.warning(f"Could not save example to database: {e}")

                        st.success(f"✓ Imported {len(examples_df)} examples ({imported_count} saved to database)")
                        st.rerun()

            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    # Display current examples
    if st.session_state.few_shot_examples:
        st.divider()
        st.write(f"**Current Examples** ({len(st.session_state.few_shot_examples)})")

        # Group by category
        examples_by_category = {}
        for example in st.session_state.few_shot_examples:
            cat = example["category"]
            if cat not in examples_by_category:
                examples_by_category[cat] = []
            examples_by_category[cat].append(example)

        # Show stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Examples", len(st.session_state.few_shot_examples))
        with col2:
            st.metric("Categories Covered", len(examples_by_category))
        with col3:
            avg_per_cat = len(st.session_state.few_shot_examples) / len(examples_by_category)
            st.metric("Avg per Category", f"{avg_per_cat:.1f}")

        # Show examples by category
        for category, examples in examples_by_category.items():
            with st.expander(f"📁 {category} ({len(examples)} examples)"):
                for i, example in enumerate(examples):
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.write(f"**{i+1}.** {example['text']}")
                        if example.get("reasoning"):
                            st.caption(f"💭 {example['reasoning']}")

                    with col2:
                        if st.button("🗑️ Remove", key=f"remove_example_{category}_{i}"):
                            st.session_state.few_shot_examples.remove(example)

                            # Delete from database if we have a session
                            if "db_session_id" in st.session_state:
                                try:
                                    # Find and delete the example from database
                                    db_examples = FewShotExampleRepository.get_session_examples(
                                        st.session_state.db_session_id,
                                        column_name=column_name
                                    )
                                    for db_ex in db_examples:
                                        if (db_ex.example_text == example["text"] and
                                            db_ex.category == example["category"]):
                                            FewShotExampleRepository.delete_example(str(db_ex.id))
                                            logger.info(f"Deleted example from database: {db_ex.id}")
                                            break
                                except Exception as e:
                                    logger.warning(f"Could not delete example from database: {e}")

                            st.rerun()

        # Clear all button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗑️ Clear All Examples", type="secondary"):
                st.session_state.few_shot_examples = []

                # Delete all from database if we have a session
                if "db_session_id" in st.session_state:
                    try:
                        count = FewShotExampleRepository.delete_session_examples(
                            st.session_state.db_session_id
                        )
                        logger.info(f"Deleted {count} examples from database")
                    except Exception as e:
                        logger.warning(f"Could not delete examples from database: {e}")

                st.rerun()

        # Return examples for use in classification
        return st.session_state.few_shot_examples

    else:
        st.info("💡 No examples added yet. Classification will use zero-shot learning.")
        return None


def format_examples_for_prompt(examples: List[Dict], column_name: str) -> str:
    """
    Format few-shot examples for inclusion in classification prompt

    Args:
        examples: List of example dictionaries
        column_name: Name of the column

    Returns:
        Formatted string for prompt
    """
    if not examples:
        return ""

    formatted = "\n**Examples:**\n"

    for i, example in enumerate(examples, 1):
        formatted += f"\n{i}. Text: \"{example['text']}\"\n"
        formatted += f"   Category: {example['category']}\n"

        if example.get("reasoning"):
            formatted += f"   Reasoning: {example['reasoning']}\n"

    formatted += "\nNow classify the following text using the same logic:\n"

    return formatted


def get_example_stats(examples: List[Dict]) -> Dict:
    """
    Get statistics about the examples

    Args:
        examples: List of example dictionaries

    Returns:
        Dictionary with statistics
    """
    if not examples:
        return {
            "total": 0,
            "categories": 0,
            "avg_per_category": 0,
            "coverage": {}
        }

    # Count by category
    coverage = {}
    for example in examples:
        cat = example["category"]
        coverage[cat] = coverage.get(cat, 0) + 1

    return {
        "total": len(examples),
        "categories": len(coverage),
        "avg_per_category": len(examples) / len(coverage) if coverage else 0,
        "coverage": coverage
    }
