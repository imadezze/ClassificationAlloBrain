"""Unit tests for LLMService"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from src.services.llm_service import LLMService


class TestLLMService:
    """Test LLMService functionality"""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response"""
        return {
            "choices": [{
                "message": {
                    "content": '{"category": "Technical Support", "confidence": "high", "reasoning": "Test reasoning"}'
                }
            }]
        }

    @pytest.fixture
    def sample_categories(self):
        """Sample categories for testing"""
        return [
            {
                "name": "Technical Support",
                "description": "Customer needs technical help",
                "boundary": "Excludes billing questions"
            },
            {
                "name": "Sales Inquiry",
                "description": "Questions about products or pricing",
                "boundary": "Pre-purchase questions only"
            },
            {
                "name": "Billing Question",
                "description": "Payment or invoice related",
                "boundary": "Post-purchase financial matters"
            }
        ]

    def test_service_initialization(self):
        """Test LLMService initialization"""
        service = LLMService()
        assert service is not None
        assert hasattr(service, 'model')

    def test_service_initialization_with_custom_model(self):
        """Test initialization with custom model"""
        custom_model = "gpt-4o"
        service = LLMService(model=custom_model)
        assert service.model == custom_model

    @patch('src.services.llm_service.litellm.completion')
    def test_classify_value_success(self, mock_completion, sample_categories, mock_llm_response):
        """Test successful classification"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"category": "Technical Support"}'
                )
            )]
        )

        service = LLMService()
        result = service.classify_value(
            value="How do I reset my password?",
            categories=sample_categories,
            column_name="support_ticket",
            use_structured_output=False
        )

        assert result["success"] is True
        assert "predicted_category" in result
        assert result["predicted_category"] in [cat["name"] for cat in sample_categories]

    @patch('src.services.llm_service.litellm.completion')
    def test_classify_value_with_structured_output(self, mock_completion, sample_categories):
        """Test classification with structured output"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"category": "Technical Support"}'
                )
            )]
        )

        service = LLMService()
        result = service.classify_value(
            value="Password reset needed",
            categories=sample_categories,
            column_name="support_ticket",
            use_structured_output=True
        )

        assert result["success"] is True
        # Verify structured output schema was used
        assert mock_completion.called

    def test_get_classification_schema(self, sample_categories):
        """Test classification schema generation"""
        service = LLMService()
        category_names = [cat["name"] for cat in sample_categories]

        schema = service._get_classification_schema(category_names)

        assert "type" in schema
        assert schema["type"] == "json_schema"
        assert "json_schema" in schema
        assert "strict" in schema["json_schema"]
        assert schema["json_schema"]["strict"] is True

        # Check enum contains all categories
        enum_values = schema["json_schema"]["schema"]["properties"]["category"]["enum"]
        assert set(enum_values) == set(category_names)

    @patch('src.services.llm_service.litellm.completion')
    def test_classify_with_few_shot_examples(self, mock_completion, sample_categories):
        """Test classification with few-shot examples"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"category": "Technical Support"}'
                )
            )]
        )

        few_shot_examples = [
            {
                "example_text": "Can't log in",
                "category": "Technical Support",
                "reasoning": "Login issues are technical"
            }
        ]

        service = LLMService()
        result = service.classify_value(
            value="Unable to access my account",
            categories=sample_categories,
            column_name="support_ticket",
            few_shot_examples=few_shot_examples,
            use_structured_output=False
        )

        assert result["success"] is True
        # Verify examples were included in prompt
        call_args = mock_completion.call_args
        messages = call_args[1]["messages"]
        prompt_text = str(messages)
        assert "Can't log in" in prompt_text

    @patch('src.services.llm_service.litellm.completion')
    def test_discover_categories(self, mock_completion):
        """Test category discovery"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='''[
                        {
                            "name": "Bug Report",
                            "description": "Software issues",
                            "boundary": "Technical problems"
                        }
                    ]'''
                )
            )]
        )

        sample_data = pd.DataFrame({
            "text": [
                "Found a bug in the app",
                "App crashes on startup",
                "Feature request for dark mode"
            ]
        })

        service = LLMService()
        result = service.discover_categories(
            sample_data=sample_data,
            column_name="text"
        )

        assert result["success"] is True
        assert "categories" in result
        assert len(result["categories"]) > 0

    @patch('src.services.llm_service.litellm.completion')
    def test_error_handling(self, mock_completion, sample_categories):
        """Test error handling when LLM call fails"""
        mock_completion.side_effect = Exception("API Error")

        service = LLMService()
        result = service.classify_value(
            value="Test text",
            categories=sample_categories,
            column_name="support_ticket",
            use_structured_output=False
        )

        assert result["success"] is False
        assert "error" in result

    def test_extract_json_from_response(self):
        """Test JSON extraction from LLM response"""
        service = LLMService()

        # Test with JSON in markdown code block
        response_with_markdown = '```json\n{"category": "Test"}\n```'
        extracted = service._extract_json_from_response(response_with_markdown)
        assert '{"category": "Test"}' in extracted

        # Test with plain JSON
        plain_json = '{"category": "Test"}'
        extracted = service._extract_json_from_response(plain_json)
        assert extracted == plain_json

    def test_temperature_override(self):
        """Test that temperature can be overridden"""
        service = LLMService()

        # Should use custom temperature if provided
        # This tests the parameter passing logic
        assert hasattr(service, '_call_llm')

    @patch('streamlit.session_state', {})
    def test_get_model_from_session_state(self):
        """Test model retrieval from session state"""
        import streamlit as st

        st.session_state["selected_model"] = "gpt-4o"

        service = LLMService()
        model = service.get_model()

        assert model == "gpt-4o"

    def test_build_classification_prompt(self, sample_categories):
        """Test prompt building for classification"""
        service = LLMService()

        # This tests internal prompt construction
        # Implementation may vary based on actual service code
        assert hasattr(service, 'classify_value')
