"""Pytest configuration and shared fixtures"""
import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_categories():
    """Reusable sample categories fixture"""
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
        },
        {
            "name": "Product Questions",
            "description": "Questions about products and features",
            "boundary": "Product information inquiries"
        }
    ]


@pytest.fixture
def sample_few_shot_examples():
    """Reusable few-shot examples fixture"""
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
            "text": "The app keeps crashing when I open it",
            "category": "Technical Support",
            "reasoning": "Software stability problem"
        },
        {
            "text": "What features are included in the premium plan?",
            "category": "Product Questions",
            "reasoning": "Product feature inquiry"
        }
    ]


@pytest.fixture
def mock_llm_response():
    """Factory fixture for creating mock LLM responses"""
    def _create_response(category: str, confidence: str = "high"):
        return {
            "category": category,
            "confidence": confidence
        }
    return _create_response
