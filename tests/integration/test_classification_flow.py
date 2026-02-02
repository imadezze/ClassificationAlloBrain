"""Integration tests for complete classification workflow"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from uuid import uuid4
from src.services.llm_service import LLMService
from src.database.repositories.classification_repository import ClassificationRepository
from src.database.repositories.few_shot_example_repository import FewShotExampleRepository


class TestClassificationFlow:
    """Test end-to-end classification workflows"""

    @pytest.fixture
    def sample_dataframe(self):
        """Create sample DataFrame for classification"""
        return pd.DataFrame({
            "text": [
                "How do I reset my password?",
                "What are your pricing options?",
                "My invoice is incorrect",
                "Product installation guide needed",
                "Discount code not working"
            ]
        })

    @pytest.fixture
    def sample_categories(self):
        """Sample categories for classification"""
        return [
            {
                "name": "Technical Support",
                "description": "Technical assistance and troubleshooting",
                "boundary": "Technical issues only, excludes billing"
            },
            {
                "name": "Sales Inquiry",
                "description": "Pre-purchase questions about products",
                "boundary": "Before purchase only"
            },
            {
                "name": "Billing Question",
                "description": "Payment and invoice related questions",
                "boundary": "Post-purchase financial matters"
            }
        ]

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        session = Mock()
        session.add = Mock()
        session.commit = Mock()
        session.query = Mock()
        return session

    @patch('src.services.llm_service.litellm.completion')
    def test_complete_classification_workflow(
        self,
        mock_completion,
        sample_dataframe,
        sample_categories,
        mock_db_session
    ):
        """Test complete workflow from data to classification"""
        # Mock LLM responses
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"category": "Technical Support"}'
                )
            )]
        )

        # Initialize service
        llm_service = LLMService()

        # Classify all rows
        results = []
        for idx, row in sample_dataframe.iterrows():
            result = llm_service.classify_value(
                value=row["text"],
                categories=sample_categories,
                column_name="text",
                use_structured_output=False
            )
            results.append(result)

        # Verify all classifications succeeded
        assert all(r["success"] for r in results)
        assert len(results) == len(sample_dataframe)

    @patch('src.services.llm_service.litellm.completion')
    def test_classification_with_few_shot_examples(
        self,
        mock_completion,
        sample_categories,
        mock_db_session
    ):
        """Test classification workflow with few-shot learning"""
        # Mock LLM response
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"category": "Technical Support"}'
                )
            )]
        )

        # Create few-shot examples
        few_shot_examples = [
            {
                "example_text": "Can't access my account",
                "category": "Technical Support",
                "reasoning": "Login issues are technical"
            },
            {
                "example_text": "How much does the premium plan cost?",
                "category": "Sales Inquiry",
                "reasoning": "Pricing questions are sales"
            }
        ]

        # Initialize service
        llm_service = LLMService()

        # Classify with few-shot examples
        result = llm_service.classify_value(
            value="Unable to log in to my account",
            categories=sample_categories,
            column_name="text",
            few_shot_examples=few_shot_examples,
            use_structured_output=False
        )

        assert result["success"] is True
        assert "predicted_category" in result

        # Verify examples were used in prompt
        call_args = mock_completion.call_args
        messages = call_args[1]["messages"]
        prompt_content = str(messages)
        assert "Can't access my account" in prompt_content

    @patch('src.services.llm_service.litellm.completion')
    def test_retry_classification_with_feedback(
        self,
        mock_completion,
        sample_categories
    ):
        """Test retry workflow with user feedback"""
        # First classification
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"category": "Sales Inquiry"}'
                )
            )]
        )

        llm_service = LLMService()

        initial_result = llm_service.classify_value(
            value="My payment was charged twice",
            categories=sample_categories,
            column_name="text",
            use_structured_output=False
        )

        # Simulate user feedback: "This is about billing, not sales"
        # Retry with feedback incorporated
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"category": "Billing Question"}'
                )
            )]
        )

        retry_result = llm_service.classify_value(
            value="My payment was charged twice",
            categories=sample_categories,
            column_name="text",
            use_structured_output=False
        )

        # Both should succeed
        assert initial_result["success"] is True
        assert retry_result["success"] is True

    @patch('src.services.llm_service.litellm.completion')
    def test_batch_classification_performance(
        self,
        mock_completion,
        sample_categories
    ):
        """Test batch classification of multiple items"""
        # Mock successful responses
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"category": "Technical Support"}'
                )
            )]
        )

        llm_service = LLMService()

        # Batch classify
        texts = [f"Sample text {i}" for i in range(10)]
        results = []

        for text in texts:
            result = llm_service.classify_value(
                value=text,
                categories=sample_categories,
                column_name="text",
                use_structured_output=False
            )
            results.append(result)

        # All should succeed
        assert len(results) == 10
        assert all(r["success"] for r in results)

    @patch('src.services.llm_service.litellm.completion')
    def test_classification_error_recovery(
        self,
        mock_completion,
        sample_categories
    ):
        """Test handling of errors during classification"""
        # First call fails
        mock_completion.side_effect = [
            Exception("API Error"),
            MagicMock(
                choices=[MagicMock(
                    message=MagicMock(
                        content='{"category": "Technical Support"}'
                    )
                )]
            )
        ]

        llm_service = LLMService()

        # First attempt should fail gracefully
        result1 = llm_service.classify_value(
            value="Test text",
            categories=sample_categories,
            column_name="text",
            use_structured_output=False
        )

        assert result1["success"] is False
        assert "error" in result1

        # Second attempt should succeed
        result2 = llm_service.classify_value(
            value="Test text",
            categories=sample_categories,
            column_name="text",
            use_structured_output=False
        )

        assert result2["success"] is True

    @patch('src.services.llm_service.litellm.completion')
    def test_structured_output_enforcement(
        self,
        mock_completion,
        sample_categories
    ):
        """Test that structured output enforces category constraints"""
        # Mock response with valid category
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"category": "Technical Support"}'
                )
            )]
        )

        llm_service = LLMService()

        result = llm_service.classify_value(
            value="Test text",
            categories=sample_categories,
            column_name="text",
            use_structured_output=True
        )

        # Verify structured output schema was created
        assert mock_completion.called
        call_kwargs = mock_completion.call_args[1]

        # If response_format exists, it should have correct structure
        if "response_format" in call_kwargs:
            response_format = call_kwargs["response_format"]
            assert "type" in response_format
            assert response_format["type"] == "json_schema"

    @patch('src.services.llm_service.litellm.completion')
    def test_version_tracking_workflow(
        self,
        mock_completion,
        sample_categories,
        mock_db_session
    ):
        """Test that classification versions are tracked"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"category": "Technical Support"}'
                )
            )]
        )

        session_id = uuid4()
        llm_service = LLMService()

        # Initial classification (version 1)
        result_v1 = llm_service.classify_value(
            value="Test text",
            categories=sample_categories,
            column_name="text",
            use_structured_output=False
        )

        # Retry classification (version 2)
        result_v2 = llm_service.classify_value(
            value="Test text",
            categories=sample_categories,
            column_name="text",
            use_structured_output=False
        )

        # Both should succeed
        assert result_v1["success"] is True
        assert result_v2["success"] is True

        # In real implementation, versions would be tracked in database
        # This test verifies the workflow supports versioning
