"""LLM Service - Interface to LiteLLM with OpenAI provider"""
import json
from typing import List, Dict, Optional
from litellm import completion
from src.config import Config


class LLMService:
    """Service for interacting with LLM via LiteLLM"""

    def __init__(self):
        """Initialize LLM service"""
        self.model = Config.LLM_MODEL
        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS

    def _call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Call LLM with messages

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override

        Returns:
            LLM response content
        """
        try:
            response = completion(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                api_key=Config.OPENAI_API_KEY,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error calling LLM: {str(e)}")

    def discover_categories(
        self, column_name: str, sample_values: List[str], num_categories: int = 5
    ) -> Dict:
        """
        Discover categories from sample data

        Args:
            column_name: Name of the column being classified
            sample_values: Sample of values from the column
            num_categories: Suggested number of categories

        Returns:
            Dictionary with discovered categories and their definitions
        """
        sample_text = "\n".join([f"- {val}" for val in sample_values[:50]])

        prompt = f"""You are a data analyst helping to categorize text data.

Column Name: {column_name}

Sample Values:
{sample_text}

Task: Analyze these sample values and suggest {num_categories} meaningful categories that would best organize this data.

For each category, provide:
1. Category Name: A clear, descriptive name
2. Description: A detailed description of what belongs in this category
3. Boundary Definition: Clear criteria for inclusion/exclusion
4. Example Values: 2-3 example values from the samples that fit this category

Return your response as a JSON array with this structure:
[
  {{
    "name": "Category Name",
    "description": "Detailed description",
    "boundary": "Clear inclusion/exclusion criteria",
    "examples": ["example1", "example2"]
  }}
]

Only return the JSON array, no other text."""

        messages = [{"role": "user", "content": prompt}]

        try:
            response = self._call_llm(messages, temperature=0.3, max_tokens=2000)

            # Extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            categories = json.loads(response)

            return {
                "success": True,
                "categories": categories,
                "column_name": column_name,
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse LLM response as JSON: {str(e)}",
                "raw_response": response,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def classify_value(
        self, value: str, categories: List[Dict], column_name: str
    ) -> Dict:
        """
        Classify a single value into one of the provided categories

        Args:
            value: Value to classify
            categories: List of category definitions
            column_name: Name of the column

        Returns:
            Dictionary with classification result
        """
        categories_text = "\n".join(
            [
                f"{i+1}. {cat['name']}: {cat['description']}\n   Boundary: {cat['boundary']}"
                for i, cat in enumerate(categories)
            ]
        )

        prompt = f"""You are a data classifier. Classify the following text into one of the provided categories.

Column: {column_name}
Text to classify: "{value}"

Available Categories:
{categories_text}

Instructions:
1. Read the text carefully
2. Match it to the most appropriate category based on the boundary definitions
3. Return ONLY the category name, nothing else

Category:"""

        messages = [{"role": "user", "content": prompt}]

        try:
            response = self._call_llm(messages, temperature=0.0, max_tokens=50)
            predicted_category = response.strip()

            # Find matching category
            matched_category = None
            for cat in categories:
                if cat["name"].lower() == predicted_category.lower():
                    matched_category = cat["name"]
                    break

            if not matched_category:
                # Try partial match
                for cat in categories:
                    if cat["name"].lower() in predicted_category.lower():
                        matched_category = cat["name"]
                        break

            return {
                "success": True,
                "value": value,
                "predicted_category": matched_category or predicted_category,
                "confidence": "high" if matched_category else "low",
            }

        except Exception as e:
            return {
                "success": False,
                "value": value,
                "error": str(e),
            }

    def classify_batch(
        self, values: List[str], categories: List[Dict], column_name: str
    ) -> List[Dict]:
        """
        Classify multiple values in batch

        Args:
            values: List of values to classify
            categories: List of category definitions
            column_name: Name of the column

        Returns:
            List of classification results
        """
        results = []
        for value in values:
            result = self.classify_value(value, categories, column_name)
            results.append(result)

        return results

    def refine_categories(
        self,
        categories: List[Dict],
        feedback: str,
        sample_values: List[str],
    ) -> Dict:
        """
        Refine categories based on user feedback

        Args:
            categories: Current categories
            feedback: User feedback on what to change
            sample_values: Sample values for context

        Returns:
            Dictionary with refined categories
        """
        categories_text = json.dumps(categories, indent=2)
        sample_text = "\n".join([f"- {val}" for val in sample_values[:30]])

        prompt = f"""You are refining category definitions based on user feedback.

Current Categories:
{categories_text}

Sample Data:
{sample_text}

User Feedback: {feedback}

Task: Refine the categories based on the feedback. Maintain the JSON structure but update names, descriptions, boundaries, or examples as needed.

Return the refined categories as a JSON array with the same structure."""

        messages = [{"role": "user", "content": prompt}]

        try:
            response = self._call_llm(messages, temperature=0.2, max_tokens=2000)

            # Extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            refined_categories = json.loads(response)

            return {
                "success": True,
                "categories": refined_categories,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
