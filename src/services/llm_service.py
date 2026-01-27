"""LLM Service - Interface to LiteLLM with OpenAI provider"""
import json
from typing import List, Dict, Optional
from litellm import completion
from src.config import Config
from src.services.prompts.prompt_loader import PromptLoader


class LLMService:
    """Service for interacting with LLM via LiteLLM"""

    def __init__(self):
        """Initialize LLM service"""
        self.model = Config.LLM_MODEL
        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS
        self.prompt_loader = PromptLoader()

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

    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON from LLM response (handles markdown code blocks)

        Args:
            response: Raw LLM response

        Returns:
            Cleaned JSON string
        """
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return response.strip()

    def _format_categories_list(self, categories: List[Dict]) -> str:
        """
        Format categories for inclusion in prompts

        Args:
            categories: List of category definitions

        Returns:
            Formatted string with categories
        """
        formatting = self.prompt_loader.get_formatting_rules("value_classification")
        format_template = formatting.get(
            "category_list_format",
            "{index}. {name}: {description}\n   Boundary: {boundary}",
        )

        categories_text = []
        for i, cat in enumerate(categories):
            formatted = format_template.format(
                index=i + 1,
                name=cat["name"],
                description=cat["description"],
                boundary=cat["boundary"],
            )
            categories_text.append(formatted)

        return "\n".join(categories_text)

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
        # Format sample values
        sample_text = "\n".join([f"- {val}" for val in sample_values[:50]])

        # Load and format prompt
        prompt_data = self.prompt_loader.format_prompt(
            "category_discovery",
            {
                "column_name": column_name,
                "sample_values": sample_text,
                "num_categories": num_categories,
            },
        )

        try:
            # Call LLM with prompt parameters
            response = self._call_llm(
                prompt_data["messages"],
                temperature=prompt_data["parameters"].get("temperature"),
                max_tokens=prompt_data["parameters"].get("max_tokens"),
            )

            # Extract and parse JSON
            json_str = self._extract_json_from_response(response)
            categories = json.loads(json_str)

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
        # Format categories list
        categories_text = self._format_categories_list(categories)

        # Load and format prompt
        prompt_data = self.prompt_loader.format_prompt(
            "value_classification",
            {
                "column_name": column_name,
                "value": value,
                "categories_list": categories_text,
            },
        )

        try:
            response = self._call_llm(
                prompt_data["messages"],
                temperature=prompt_data["parameters"].get("temperature"),
                max_tokens=prompt_data["parameters"].get("max_tokens"),
            )
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
        # For now, use sequential classification
        # TODO: Implement true batch classification with batch_classification prompt
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
        # Format data
        categories_json = json.dumps(categories, indent=2)
        sample_text = "\n".join([f"- {val}" for val in sample_values[:30]])

        # Load and format prompt
        prompt_data = self.prompt_loader.format_prompt(
            "category_refinement",
            {
                "current_categories": categories_json,
                "sample_values": sample_text,
                "feedback": feedback,
            },
        )

        try:
            response = self._call_llm(
                prompt_data["messages"],
                temperature=prompt_data["parameters"].get("temperature"),
                max_tokens=prompt_data["parameters"].get("max_tokens"),
            )

            # Extract and parse JSON
            json_str = self._extract_json_from_response(response)
            refined_categories = json.loads(json_str)

            return {
                "success": True,
                "categories": refined_categories,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
