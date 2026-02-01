"""Tests for Few-Shot Examples Integration"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.llm_service import LLMService
from src.ui.components.few_shot_examples import format_examples_for_prompt, get_example_stats


class TestFewShotExamplesIntegration:
    """Test few-shot examples integration with prompts"""

    @pytest.fixture
    def sample_categories(self):
        """Sample categories for testing"""
        return [
            {
                "name": "Account Access & Login",
                "description": "Issues with logging in, passwords, account access",
                "boundary": "Authentication and access control issues"
            },
            {
                "name": "Billing & Payments",
                "description": "Payment issues, invoices, refunds",
                "boundary": "Financial transactions and billing"
            },
            {
                "name": "Technical Support",
                "description": "Technical issues, bugs, performance problems",
                "boundary": "Software functionality and performance"
            }
        ]

    @pytest.fixture
    def sample_examples(self):
        """Sample few-shot examples"""
        return [
            {
                "text": "I can't log into my account",
                "category": "Account Access & Login",
                "reasoning": "User authentication issue"
            },
            {
                "text": "My credit card was charged twice",
                "category": "Billing & Payments",
                "reasoning": "Duplicate payment issue"
            },
            {
                "text": "The app keeps crashing",
                "category": "Technical Support",
                "reasoning": "Software stability problem"
            }
        ]

    def test_format_examples_for_prompt(self, sample_examples):
        """Test that examples are formatted correctly for prompt"""
        formatted = format_examples_for_prompt(sample_examples, "issue_description")

        # Check that all examples are included
        assert "I can't log into my account" in formatted
        assert "My credit card was charged twice" in formatted
        assert "The app keeps crashing" in formatted

        # Check that categories are included
        assert "Account Access & Login" in formatted
        assert "Billing & Payments" in formatted
        assert "Technical Support" in formatted

        # Check that reasoning is included
        assert "User authentication issue" in formatted
        assert "Duplicate payment issue" in formatted

        # Check that examples are numbered
        assert "1." in formatted
        assert "2." in formatted
        assert "3." in formatted

    def test_examples_in_classify_value_prompt(self, sample_categories, sample_examples):
        """Test that examples are integrated into classify_value prompt"""
        llm_service = LLMService()

        # Mock the LLM call to capture the prompt
        original_call_llm = llm_service._call_llm
        captured_prompt = None

        def mock_call_llm(messages, **kwargs):
            nonlocal captured_prompt
            captured_prompt = messages
            # Return a mock response
            return '{"category": "Account Access & Login", "confidence": "high"}'

        llm_service._call_llm = mock_call_llm

        # Call classify_value with examples
        result = llm_service.classify_value(
            value="Reset password not working",
            categories=sample_categories,
            column_name="issue_description",
            few_shot_examples=sample_examples,
            use_structured_output=True
        )

        # Check that the prompt was captured
        assert captured_prompt is not None

        # Check that examples are in the user message
        user_message = captured_prompt[1]["content"]
        assert "Examples for guidance:" in user_message
        assert "I can't log into my account" in user_message
        assert "Account Access & Login" in user_message
        assert "User authentication issue" in user_message

        # Restore original method
        llm_service._call_llm = original_call_llm

    def test_examples_without_reasoning(self):
        """Test that examples work without reasoning field"""
        examples = [
            {
                "text": "Password reset",
                "category": "Account Access & Login"
            }
        ]

        formatted = format_examples_for_prompt(examples, "issue")

        assert "Password reset" in formatted
        assert "Account Access & Login" in formatted
        # Should not crash without reasoning

    def test_empty_examples(self):
        """Test behavior with empty examples list"""
        formatted = format_examples_for_prompt([], "issue")

        # Should return empty string or handle gracefully
        assert formatted == ""

    def test_get_example_stats(self, sample_examples):
        """Test example statistics calculation"""
        stats = get_example_stats(sample_examples)

        assert stats["total"] == 3
        assert stats["categories"] == 3
        assert stats["avg_per_category"] == 1.0
        assert "Account Access & Login" in stats["coverage"]
        assert stats["coverage"]["Account Access & Login"] == 1

    def test_get_example_stats_empty(self):
        """Test stats with empty examples"""
        stats = get_example_stats([])

        assert stats["total"] == 0
        assert stats["categories"] == 0
        assert stats["avg_per_category"] == 0

    def test_classify_value_with_feedback_and_examples(self, sample_categories, sample_examples):
        """Test that both feedback and examples are included in prompt"""
        llm_service = LLMService()

        captured_prompt = None

        def mock_call_llm(messages, **kwargs):
            nonlocal captured_prompt
            captured_prompt = messages
            return '{"category": "Technical Support", "confidence": "medium"}'

        llm_service._call_llm = mock_call_llm

        # Call with both feedback and examples
        result = llm_service.classify_value_with_feedback(
            value="App is slow",
            categories=sample_categories,
            column_name="issue",
            feedback="Focus on performance issues",
            few_shot_examples=sample_examples,
            use_structured_output=True
        )

        # Check that both examples and feedback are in prompt
        user_message = captured_prompt[1]["content"]
        assert "Examples for guidance:" in user_message
        assert "The app keeps crashing" in user_message
        assert "Additional guidance: Focus on performance issues" in user_message


class TestFewShotPromptConstruction:
    """Test prompt construction details"""

    def test_example_insertion_position(self):
        """Test that examples are inserted before 'Text to classify:'"""
        llm_service = LLMService()

        examples = [
            {
                "text": "Example text",
                "category": "Test Category"
            }
        ]

        categories = [
            {
                "name": "Test Category",
                "description": "Test",
                "boundary": "Test boundary"
            }
        ]

        captured_prompt = None

        def mock_call_llm(messages, **kwargs):
            nonlocal captured_prompt
            captured_prompt = messages
            return '{"category": "Test Category", "confidence": "high"}'

        llm_service._call_llm = mock_call_llm

        llm_service.classify_value(
            value="Test value",
            categories=categories,
            column_name="test_column",
            few_shot_examples=examples,
            use_structured_output=True
        )

        user_message = captured_prompt[1]["content"]

        # Examples should come before "Text to classify:"
        examples_pos = user_message.find("Examples for guidance:")
        classify_pos = user_message.find("Text to classify:")

        assert examples_pos < classify_pos, "Examples should come before the text to classify"

    def test_multiple_examples_formatting(self):
        """Test formatting with multiple examples per category"""
        examples = [
            {"text": "Example 1", "category": "Cat A"},
            {"text": "Example 2", "category": "Cat A"},
            {"text": "Example 3", "category": "Cat B"},
        ]

        formatted = format_examples_for_prompt(examples, "column")

        # All examples should be numbered sequentially
        assert "1. Text:" in formatted
        assert "2. Text:" in formatted
        assert "3. Text:" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
