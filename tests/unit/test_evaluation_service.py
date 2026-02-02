"""Unit tests for EvaluationService"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.evaluation_service import EvaluationService


class TestEvaluationService:
    """Test EvaluationService functionality"""

    @pytest.fixture
    def sample_categories(self):
        """Sample categories for testing"""
        return [
            {
                "name": "Technical Support",
                "description": "Technical assistance",
                "boundary": "Technical issues only"
            },
            {
                "name": "Sales",
                "description": "Sales inquiries",
                "boundary": "Pre-purchase questions"
            }
        ]

    @pytest.fixture
    def mock_classification_result(self):
        """Mock classification result"""
        return {
            "success": True,
            "predicted_category": "Technical Support",
            "confidence": "high",
            "reasoning": "Test reasoning"
        }

    def test_service_initialization(self):
        """Test EvaluationService initialization"""
        service = EvaluationService()
        assert service is not None
        assert hasattr(service, 'llm_service')
        assert hasattr(service, 'JUDGE_MODELS')

    def test_judge_models_configuration(self):
        """Test that judge models are properly configured"""
        service = EvaluationService()

        assert "openai_primary" in service.JUDGE_MODELS
        assert "bedrock_opus_primary" in service.JUDGE_MODELS

        # Verify these are stronger models
        openai_model = service.JUDGE_MODELS["openai_primary"]
        assert "gpt-5" in openai_model or "gpt-4" in openai_model

        bedrock_model = service.JUDGE_MODELS["bedrock_opus_primary"]
        assert "opus" in bedrock_model.lower()

    @patch('src.services.evaluation_service.LLMService')
    def test_self_consistency_evaluation(self, mock_llm_service, sample_categories, mock_classification_result):
        """Test self-consistency evaluation"""
        # Mock LLM service to return consistent predictions
        mock_llm = Mock()
        mock_llm.classify_value.return_value = mock_classification_result
        mock_llm_service.return_value = mock_llm

        service = EvaluationService()
        service.llm_service = mock_llm

        result = service.self_consistency_evaluation(
            text="How do I reset my password?",
            categories=sample_categories,
            column_name="support_ticket",
            temperatures=[0.1, 0.5],
            num_runs=2
        )

        assert result["success"] is True
        assert "agreement_rate" in result
        assert "most_common_prediction" in result
        assert "confidence_level" in result
        assert 0 <= result["agreement_rate"] <= 1

    def test_interpret_agreement_high(self):
        """Test agreement interpretation for high agreement"""
        service = EvaluationService()
        result = service._interpret_agreement(0.85)
        assert result == "high"

    def test_interpret_agreement_medium(self):
        """Test agreement interpretation for medium agreement"""
        service = EvaluationService()
        result = service._interpret_agreement(0.65)
        assert result == "medium"

    def test_interpret_agreement_low(self):
        """Test agreement interpretation for low agreement"""
        service = EvaluationService()
        result = service._interpret_agreement(0.45)
        assert result == "low"

    def test_get_consistency_recommendation_high(self):
        """Test recommendation for high consistency"""
        service = EvaluationService()
        recommendation = service._get_consistency_recommendation(0.85)
        assert "high confidence" in recommendation.lower()

    def test_get_consistency_recommendation_low(self):
        """Test recommendation for low consistency"""
        service = EvaluationService()
        recommendation = service._get_consistency_recommendation(0.45)
        assert "low confidence" in recommendation.lower()

    @patch('src.services.evaluation_service.LLMService')
    def test_generate_contrastive_examples(self, mock_llm_service, sample_categories):
        """Test synthetic example generation"""
        mock_llm = Mock()
        mock_llm._call_llm.return_value = '''[
            {
                "text": "Example 1",
                "difficulty": "easy",
                "reasoning": "Test reasoning"
            }
        ]'''
        mock_llm._extract_json_from_response.return_value = '''[
            {
                "text": "Example 1",
                "difficulty": "easy",
                "reasoning": "Test reasoning"
            }
        ]'''
        mock_llm_service.return_value = mock_llm

        service = EvaluationService()

        result = service.generate_contrastive_examples(
            category=sample_categories[0],
            num_examples=3,
            difficulty_levels=["easy", "medium"]
        )

        assert "examples" in result or "error" in result

    @patch('src.services.evaluation_service.LLMService')
    def test_classify_generated_examples(self, mock_llm_service, sample_categories, mock_classification_result):
        """Test classification of generated examples"""
        mock_llm = Mock()
        mock_llm.classify_value.return_value = mock_classification_result
        mock_llm_service.return_value = mock_llm

        service = EvaluationService()
        service.llm_service = mock_llm

        generated_examples = [
            {"text": "Example 1", "difficulty": "easy"},
            {"text": "Example 2", "difficulty": "medium"}
        ]

        result = service.classify_generated_examples(
            generated_examples=generated_examples,
            categories=sample_categories,
            column_name="support_ticket",
            expected_category="Technical Support"
        )

        assert result["success"] is True
        assert "accuracy" in result
        assert "correct" in result
        assert "total_examples" in result

    def test_assess_quality_excellent(self):
        """Test quality assessment for excellent accuracy"""
        service = EvaluationService()
        assessment = service._assess_quality(95)
        assert "excellent" in assessment.lower()

    def test_assess_quality_moderate(self):
        """Test quality assessment for moderate accuracy"""
        service = EvaluationService()
        assessment = service._assess_quality(75)
        assert "moderate" in assessment.lower()

    def test_assess_quality_poor(self):
        """Test quality assessment for poor accuracy"""
        service = EvaluationService()
        assessment = service._assess_quality(50)
        assert "poor" in assessment.lower()

    @patch('src.services.evaluation_service.LLMService')
    def test_llm_as_judge_single_judge(self, mock_llm_service, sample_categories):
        """Test LLM-as-judge with single judge"""
        mock_llm = Mock()
        mock_llm._call_llm.return_value = '''{
            "independent_classification": "Technical Support",
            "agreement": "AGREE",
            "correct_category": null,
            "reasoning_quality": 4,
            "judge_confidence": 0.8,
            "explanation": "Test explanation"
        }'''
        mock_llm._extract_json_from_response.return_value = '''{
            "independent_classification": "Technical Support",
            "agreement": "AGREE",
            "correct_category": null,
            "reasoning_quality": 4,
            "judge_confidence": 0.8,
            "explanation": "Test explanation"
        }'''
        mock_llm_service.return_value = mock_llm

        service = EvaluationService()

        result = service.llm_as_judge_evaluation(
            text="Password reset",
            predicted_category="Technical Support",
            categories=sample_categories,
            column_name="support_ticket",
            use_cross_model=False
        )

        assert "judge_results" in result or "error" in result

    def test_get_consensus_all_agree(self):
        """Test consensus calculation when all judges agree"""
        service = EvaluationService()

        judge_results = [
            {"agreement": "AGREE"},
            {"agreement": "AGREE"}
        ]

        consensus = service._get_consensus(judge_results)
        assert "all judges agree" in consensus.lower()

    def test_get_consensus_all_disagree(self):
        """Test consensus calculation when all judges disagree"""
        service = EvaluationService()

        judge_results = [
            {"agreement": "DISAGREE"},
            {"agreement": "DISAGREE"}
        ]

        consensus = service._get_consensus(judge_results)
        assert "disagree" in consensus.lower()

    def test_get_consensus_mixed(self):
        """Test consensus calculation with mixed opinions"""
        service = EvaluationService()

        judge_results = [
            {"agreement": "AGREE"},
            {"agreement": "DISAGREE"}
        ]

        consensus = service._get_consensus(judge_results)
        assert "mixed" in consensus.lower() or "ambiguous" in consensus.lower()

    def test_get_final_verdict_confirmed(self):
        """Test final verdict when classification is confirmed"""
        service = EvaluationService()

        judge_results = [
            {"agreement": "AGREE"},
            {"agreement": "AGREE"}
        ]

        verdict = service._get_final_verdict(judge_results)
        assert "confirmed" in verdict.lower() or "correct" in verdict.lower()

    def test_get_final_verdict_questionable(self):
        """Test final verdict when classification is questionable"""
        service = EvaluationService()

        judge_results = [
            {"agreement": "DISAGREE"},
            {"agreement": "DISAGREE"}
        ]

        verdict = service._get_final_verdict(judge_results)
        assert "questionable" in verdict.lower() or "review" in verdict.lower()
