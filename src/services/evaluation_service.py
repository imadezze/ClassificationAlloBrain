"""Evaluation Service - Comprehensive classification evaluation framework"""
import logging
from typing import List, Dict, Optional, Tuple
from collections import Counter
import statistics
from src.services.llm_service import LLMService
from src.config import Config

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluating classification quality using multiple methods"""

    # Best models for judging (stronger than classification models)
    JUDGE_MODELS = {
        "openai_primary": "gpt-5.2-2025-12-11",
        "openai_secondary": "gpt-4.1",
        "anthropic_primary": "claude-opus-4-5-20251101",  # Direct API
        "anthropic_secondary": "claude-sonnet-4-5-20250929",  # Direct API
        "bedrock_opus_primary": "bedrock/global.anthropic.claude-opus-4-5-20251101-v1:0",  # Bedrock Opus 4.5 Global
        "bedrock_opus_regional": "bedrock/anthropic.claude-opus-4-5-20251101-v1:0",  # Bedrock Opus 4.5 Regional
        "bedrock_primary": "bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0",  # Bedrock Sonnet 4.5
        "bedrock_secondary": "bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Bedrock 3.7
    }

    def __init__(self):
        """Initialize evaluation service"""
        self.llm_service = LLMService()

    def self_consistency_evaluation(
        self,
        text: str,
        categories: List[Dict],
        column_name: str,
        temperatures: List[float] = [0.1, 0.5, 0.9],
        num_runs: int = 3
    ) -> Dict:
        """
        Evaluate classification consistency across multiple runs with different temperatures

        Args:
            text: Text to classify
            categories: List of category definitions
            column_name: Column name
            temperatures: List of temperatures to test
            num_runs: Number of runs per temperature

        Returns:
            Dictionary with consistency results
        """
        results = []
        all_predictions = []

        for temp in temperatures:
            for run in range(num_runs):
                try:
                    # Temporarily override temperature
                    result = self.llm_service.classify_value(
                        value=text,
                        categories=categories,
                        column_name=column_name,
                        use_structured_output=True
                    )

                    if result["success"]:
                        prediction = result["predicted_category"]
                        all_predictions.append(prediction)
                        results.append({
                            "temperature": temp,
                            "run": run + 1,
                            "prediction": prediction,
                            "confidence": result.get("confidence", "medium")
                        })

                except Exception as e:
                    logger.error(f"Error in consistency eval: {e}")

        # Calculate agreement
        if not all_predictions:
            return {"success": False, "error": "No predictions obtained"}

        # Count consensus
        prediction_counts = Counter(all_predictions)
        most_common_prediction, count = prediction_counts.most_common(1)[0]
        total_runs = len(all_predictions)
        agreement_rate = count / total_runs

        # Calculate confidence calibration
        reported_confidences = [r.get("confidence", "medium") for r in results]

        return {
            "success": True,
            "text": text,
            "total_runs": total_runs,
            "predictions": dict(prediction_counts),
            "most_common_prediction": most_common_prediction,
            "agreement_rate": agreement_rate,
            "agreement_count": f"{count}/{total_runs}",
            "confidence_level": self._interpret_agreement(agreement_rate),
            "detailed_results": results,
            "recommendation": self._get_consistency_recommendation(agreement_rate)
        }

    def _interpret_agreement(self, agreement_rate: float) -> str:
        """Interpret agreement rate"""
        if agreement_rate >= 0.8:
            return "high"
        elif agreement_rate >= 0.6:
            return "medium"
        else:
            return "low"

    def _get_consistency_recommendation(self, agreement_rate: float) -> str:
        """Get recommendation based on consistency"""
        if agreement_rate >= 0.8:
            return "High confidence - likely correct classification"
        elif agreement_rate >= 0.6:
            return "Medium confidence - some uncertainty, consider human review"
        else:
            return "Low confidence - high uncertainty, flag for human review"

    def generate_contrastive_examples(
        self,
        category: Dict,
        num_examples: int = 5,
        difficulty_levels: List[str] = ["easy", "medium", "hard"]
    ) -> Dict:
        """
        Generate synthetic examples for a category using strong models

        Args:
            category: Category definition
            num_examples: Number of examples to generate
            difficulty_levels: Difficulty levels to include

        Returns:
            Dictionary with generated examples
        """
        judge_model = self.JUDGE_MODELS["bedrock_opus_primary"]

        prompt = f"""Generate {num_examples} realistic examples that belong to this category:

Category: {category['name']}
Description: {category['description']}
Boundary: {category.get('boundary', 'Not specified')}

Requirements:
- Generate diverse, realistic examples
- Include different difficulty levels: {', '.join(difficulty_levels)}
- Each example should clearly belong to this category
- Vary the phrasing and context

Return a JSON array of objects with:
- text: The example text
- difficulty: easy/medium/hard
- reasoning: Why this belongs to the category

Example format:
[
  {{
    "text": "Example text here",
    "difficulty": "medium",
    "reasoning": "This belongs to {category['name']} because..."
  }}
]
"""

        try:
            llm = LLMService(model=judge_model)
            response = llm._call_llm(
                messages=[
                    {"role": "system", "content": "You are an expert at generating test examples for classification."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            # Parse JSON response
            import json
            examples = json.loads(llm._extract_json_from_response(response))

            return {
                "success": True,
                "category": category["name"],
                "examples": examples,
                "judge_model": judge_model
            }

        except Exception as e:
            logger.error(f"Error generating contrastive examples: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def classify_generated_examples(
        self,
        generated_examples: List[Dict],
        categories: List[Dict],
        column_name: str,
        expected_category: str
    ) -> Dict:
        """
        Classify generated examples and check if they match expected category

        Args:
            generated_examples: List of generated examples
            categories: All categories
            column_name: Column name
            expected_category: Expected category for all examples

        Returns:
            Accuracy metrics
        """
        results = []
        correct = 0
        total = len(generated_examples)

        for example in generated_examples:
            try:
                classification = self.llm_service.classify_value(
                    value=example["text"],
                    categories=categories,
                    column_name=column_name,
                    use_structured_output=True
                )

                is_correct = classification["predicted_category"] == expected_category

                if is_correct:
                    correct += 1

                results.append({
                    "text": example["text"],
                    "difficulty": example.get("difficulty", "unknown"),
                    "expected": expected_category,
                    "predicted": classification["predicted_category"],
                    "correct": is_correct,
                    "confidence": classification.get("confidence", "unknown")
                })

            except Exception as e:
                logger.error(f"Error classifying example: {e}")

        accuracy = (correct / total * 100) if total > 0 else 0

        return {
            "success": True,
            "total_examples": total,
            "correct": correct,
            "accuracy": accuracy,
            "quality_assessment": self._assess_quality(accuracy),
            "results": results
        }

    def _assess_quality(self, accuracy: float) -> str:
        """Assess classification quality based on accuracy"""
        if accuracy >= 90:
            return "Excellent - Good classification capability"
        elif accuracy >= 70:
            return "Moderate - Needs refinement"
        else:
            return "Poor - Serious issues, review category definitions"

    def llm_as_judge_evaluation(
        self,
        text: str,
        predicted_category: str,
        categories: List[Dict],
        column_name: str,
        confidence: Optional[str] = None,
        reasoning: Optional[str] = None,
        use_cross_model: bool = True
    ) -> Dict:
        """
        Use stronger models to judge classification quality

        Args:
            text: Original text
            predicted_category: Category predicted by classifier
            categories: All categories
            column_name: Column name
            confidence: Reported confidence
            reasoning: Classifier's reasoning (if available)
            use_cross_model: Use multiple judge models

        Returns:
            Judge evaluation results
        """
        judges = [
            ("bedrock_opus_primary", self.JUDGE_MODELS["bedrock_opus_primary"]),
            ("openai_primary", self.JUDGE_MODELS["openai_primary"])
        ] if use_cross_model else [("bedrock_opus_primary", self.JUDGE_MODELS["bedrock_opus_primary"])]

        judge_results = []

        for judge_name, judge_model in judges:
            try:
                result = self._single_judge_evaluation(
                    text=text,
                    predicted_category=predicted_category,
                    categories=categories,
                    column_name=column_name,
                    confidence=confidence,
                    reasoning=reasoning,
                    judge_model=judge_model
                )

                result["judge_name"] = judge_name
                judge_results.append(result)

            except Exception as e:
                logger.error(f"Error in judge evaluation ({judge_name}): {e}")

        # Aggregate results
        if not judge_results:
            return {"success": False, "error": "No judge results obtained"}

        agreements = [r["agreement"] for r in judge_results]
        agreement_count = sum(1 for a in agreements if a == "AGREE")
        total_judges = len(judge_results)

        return {
            "success": True,
            "text": text,
            "predicted_category": predicted_category,
            "total_judges": total_judges,
            "agreement_count": agreement_count,
            "agreement_rate": agreement_count / total_judges,
            "consensus": self._get_consensus(judge_results),
            "judge_results": judge_results,
            "final_verdict": self._get_final_verdict(judge_results)
        }

    def _single_judge_evaluation(
        self,
        text: str,
        predicted_category: str,
        categories: List[Dict],
        column_name: str,
        confidence: Optional[str],
        reasoning: Optional[str],
        judge_model: str
    ) -> Dict:
        """Single judge model evaluation"""

        categories_text = "\n".join([
            f"- {cat['name']}: {cat['description']}"
            for cat in categories
        ])

        prompt = f"""You are an expert evaluator. Evaluate if the classifier made the correct decision.

Text to classify: "{text}"
Column: {column_name}

Available categories:
{categories_text}

Classifier's prediction: {predicted_category}
Classifier's confidence: {confidence or 'Not provided'}
{f"Classifier's reasoning: {reasoning}" if reasoning else ''}

Your task:
1. Independently classify this text (without bias from the classifier's choice)
2. Evaluate if you agree with the classifier
3. Rate the quality of classification

Respond in JSON format:
{{
  "independent_classification": "your category choice",
  "agreement": "AGREE" | "DISAGREE" | "PARTIALLY_AGREE",
  "correct_category": "category name if you disagree, null otherwise",
  "reasoning_quality": 1-5,
  "issues_identified": ["issue1", "issue2"],
  "judge_confidence": 0.0-1.0,
  "explanation": "your reasoning"
}}
"""

        llm = LLMService(model=judge_model)
        response = llm._call_llm(
            messages=[
                {"role": "system", "content": "You are an expert classification evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        import json
        return json.loads(llm._extract_json_from_response(response))

    def _get_consensus(self, judge_results: List[Dict]) -> str:
        """Get consensus from multiple judges"""
        agreements = [r["agreement"] for r in judge_results]
        agree_count = sum(1 for a in agreements if a == "AGREE")
        total = len(judge_results)

        if agree_count == total:
            return "All judges agree - high confidence"
        elif agree_count >= total / 2:
            return "Majority agree - moderate confidence"
        elif agree_count == 0:
            return "All judges disagree - likely error"
        else:
            return "Mixed opinions - genuinely ambiguous"

    def _get_final_verdict(self, judge_results: List[Dict]) -> str:
        """Get final verdict from judge evaluations"""
        agree_count = sum(1 for r in judge_results if r["agreement"] == "AGREE")
        total = len(judge_results)

        if agree_count == total:
            return "Classification confirmed correct"
        elif agree_count >= total / 2:
            return "Classification likely correct"
        else:
            return "Classification questionable - review needed"
