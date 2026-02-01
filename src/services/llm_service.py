"""LLM Service - Interface to LiteLLM with OpenAI provider"""
import json
import logging
from typing import List, Dict, Optional
from litellm import completion
from src.config import Config
from src.services.prompts.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


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
        response_format: Optional[Dict] = None,
    ) -> str:
        """
        Call LLM with messages

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            response_format: Optional response format (for structured outputs)

        Returns:
            LLM response content
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
                "api_key": Config.OPENAI_API_KEY,
            }

            # Add response_format if provided
            if response_format:
                kwargs["response_format"] = response_format

            response = completion(**kwargs)

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

    def _get_category_schema(self, num_categories: int) -> Dict:
        """
        Generate JSON schema for category discovery with exact array length

        Args:
            num_categories: Exact number of categories required

        Returns:
            JSON schema dictionary
        """
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "category_discovery",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "categories": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "boundary": {"type": "string"},
                                    "examples": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["name", "description", "boundary", "examples"],
                                "additionalProperties": False
                            },
                            "minItems": num_categories,
                            "maxItems": num_categories
                        }
                    },
                    "required": ["categories"],
                    "additionalProperties": False
                }
            }
        }

    def discover_categories(
        self, column_name: str, sample_values: List[str], num_categories: int = 5,
        max_retries: int = 2, progress_callback = None, use_structured_output: bool = True
    ) -> Dict:
        """
        Discover categories from sample data with retry mechanism

        Args:
            column_name: Name of the column being classified
            sample_values: Sample of values from the column
            num_categories: Suggested number of categories
            max_retries: Maximum number of retries if wrong count returned
            progress_callback: Optional callback function to report progress (for UI updates)
            use_structured_output: Use OpenAI structured outputs for guaranteed schema compliance

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

        for attempt in range(max_retries + 1):
            try:
                if progress_callback and attempt > 0:
                    progress_callback(f"Retrying... (Attempt {attempt + 1}/{max_retries + 1})")

                # Try using structured outputs if enabled and supported
                response_format = None
                if use_structured_output and self.model.startswith("gpt"):
                    try:
                        response_format = self._get_category_schema(num_categories)
                        logger.info(f"Using structured outputs with exact count: {num_categories}")
                    except Exception as e:
                        logger.warning(f"Structured outputs not available: {e}, falling back to standard mode")

                # Call LLM with prompt parameters
                response = self._call_llm(
                    prompt_data["messages"],
                    temperature=prompt_data["parameters"].get("temperature"),
                    max_tokens=prompt_data["parameters"].get("max_tokens"),
                    response_format=response_format
                )

                # Extract and parse JSON
                if response_format:
                    # Structured output returns already parsed JSON in specific format
                    if isinstance(response, str):
                        json_str = self._extract_json_from_response(response)
                        result = json.loads(json_str)
                    else:
                        result = response if isinstance(response, dict) else json.loads(response)

                    # Extract categories from structured format
                    categories = result.get("categories", result) if isinstance(result, dict) else result
                else:
                    json_str = self._extract_json_from_response(response)
                    categories = json.loads(json_str)

                # Check if we got the correct number of categories
                if len(categories) == num_categories:
                    logger.info(f"Successfully discovered {num_categories} categories on attempt {attempt + 1}")
                    return {
                        "success": True,
                        "categories": categories,
                        "column_name": column_name,
                        "attempts": attempt + 1,
                    }
                else:
                    # Wrong number of categories
                    logger.warning(
                        f"Attempt {attempt + 1}: LLM returned {len(categories)} categories, "
                        f"expected {num_categories}"
                    )

                    if attempt < max_retries:
                        # Will retry
                        continue
                    else:
                        # Last attempt - trim to requested number
                        logger.warning(
                            f"Final attempt: Using first {num_categories} of {len(categories)} categories"
                        )
                        categories = categories[:num_categories]
                        return {
                            "success": True,
                            "categories": categories,
                            "column_name": column_name,
                            "attempts": attempt + 1,
                            "warning": f"LLM returned {len(categories)} categories, trimmed to {num_categories}"
                        }

            except json.JSONDecodeError as e:
                logger.warning(f"Attempt {attempt + 1}: JSON parse error - {str(e)}")
                if attempt < max_retries:
                    continue
                return {
                    "success": False,
                    "error": f"Failed to parse LLM response as JSON: {str(e)}",
                }
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}: Error - {str(e)}")
                if attempt < max_retries:
                    continue
                return {"success": False, "error": str(e)}

        return {"success": False, "error": "Max retries exceeded"}

    def _get_classification_schema(self, category_names: List[str]) -> Dict:
        """
        Generate JSON schema for classification with strict enum constraint

        Args:
            category_names: List of exact category names to choose from

        Returns:
            JSON schema dictionary with strict enum enforcement
        """
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "classification_result",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": category_names,
                            "description": "The selected category - MUST be exactly one of the provided enum values"
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "Confidence level of the classification"
                        }
                    },
                    "required": ["category", "confidence"],
                    "additionalProperties": False
                }
            }
        }

    def classify_value(
        self, value: str, categories: List[Dict], column_name: str,
        use_structured_output: bool = True, few_shot_examples: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Classify a single value into one of the provided categories

        Args:
            value: Value to classify
            categories: List of category definitions
            column_name: Name of the column
            use_structured_output: Use structured outputs with enum constraint (default: True)
            few_shot_examples: Optional list of example classifications to guide the model

        Returns:
            Dictionary with classification result
        """
        # Extract category names for enum constraint
        category_names = [cat["name"] for cat in categories]

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

        # Add few-shot examples to prompt if provided
        if few_shot_examples:
            examples_text = "\n\n**Examples for guidance:**\n"
            for i, example in enumerate(few_shot_examples, 1):
                examples_text += f"\n{i}. Text: \"{example['text']}\"\n"
                examples_text += f"   Correct Category: {example['category']}\n"
                if example.get("reasoning"):
                    examples_text += f"   Reasoning: {example['reasoning']}\n"

            examples_text += "\nNow classify the following text using the same logic:\n"

            # Insert examples before the value
            user_message = prompt_data["messages"][1]["content"]
            # Find where to insert (before "Text to classify:")
            insert_pos = user_message.find("Text to classify:")
            if insert_pos != -1:
                prompt_data["messages"][1]["content"] = (
                    user_message[:insert_pos] +
                    examples_text +
                    user_message[insert_pos:]
                )

            logger.debug(f"Using {len(few_shot_examples)} few-shot examples for classification")

        try:
            # Use structured outputs if enabled and using GPT model
            response_format = None
            if use_structured_output and self.model.startswith("gpt"):
                response_format = self._get_classification_schema(category_names)
                logger.debug(f"Using structured outputs with {len(category_names)} category enum")

            response = self._call_llm(
                prompt_data["messages"],
                temperature=prompt_data["parameters"].get("temperature"),
                max_tokens=prompt_data["parameters"].get("max_tokens"),
                response_format=response_format
            )

            # Parse response based on whether structured outputs were used
            if response_format:
                # Structured output returns JSON
                if isinstance(response, str):
                    result = json.loads(response)
                else:
                    result = response

                predicted_category = result.get("category")
                confidence = result.get("confidence", "medium")
            else:
                # Standard output - just category name
                predicted_category = response.strip()
                confidence = None

                # Find matching category (fallback for non-structured mode)
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

                predicted_category = matched_category or predicted_category

            return {
                "success": True,
                "value": value,
                "predicted_category": predicted_category,
                "confidence": confidence if confidence else ("high" if predicted_category in category_names else "low"),
            }

        except Exception as e:
            return {
                "success": False,
                "value": value,
                "error": str(e),
            }

    def classify_value_with_feedback(
        self, value: str, categories: List[Dict], column_name: str,
        feedback: str, use_structured_output: bool = True,
        few_shot_examples: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Classify a value with additional user feedback

        Args:
            value: Value to classify
            categories: List of category definitions
            column_name: Name of the column
            feedback: User feedback to guide classification
            use_structured_output: Use structured outputs with enum constraint

        Returns:
            Dictionary with classification result
        """
        # Extract category names for enum constraint
        category_names = [cat["name"] for cat in categories]

        # Format categories list
        categories_text = self._format_categories_list(categories)

        # Load and format prompt with feedback
        prompt_data = self.prompt_loader.format_prompt(
            "value_classification",
            {
                "column_name": column_name,
                "value": value,
                "categories_list": categories_text,
            },
        )

        # Add few-shot examples to prompt if provided
        if few_shot_examples:
            examples_text = "\n\n**Examples for guidance:**\n"
            for i, example in enumerate(few_shot_examples, 1):
                examples_text += f"\n{i}. Text: \"{example['text']}\"\n"
                examples_text += f"   Correct Category: {example['category']}\n"
                if example.get("reasoning"):
                    examples_text += f"   Reasoning: {example['reasoning']}\n"

            examples_text += "\nNow classify the following text using the same logic:\n"

            # Insert examples before the value
            user_message = prompt_data["messages"][1]["content"]
            insert_pos = user_message.find("Text to classify:")
            if insert_pos != -1:
                prompt_data["messages"][1]["content"] = (
                    user_message[:insert_pos] +
                    examples_text +
                    user_message[insert_pos:]
                )

        # Add feedback to the user message
        if feedback:
            user_message = prompt_data["messages"][1]["content"]
            user_message += f"\n\nAdditional guidance: {feedback}"
            prompt_data["messages"][1]["content"] = user_message

        try:
            # Use structured outputs if enabled and using GPT model
            response_format = None
            if use_structured_output and self.model.startswith("gpt"):
                response_format = self._get_classification_schema(category_names)
                logger.debug(f"Reclassifying with feedback using {len(category_names)} category enum")

            response = self._call_llm(
                prompt_data["messages"],
                temperature=prompt_data["parameters"].get("temperature"),
                max_tokens=prompt_data["parameters"].get("max_tokens"),
                response_format=response_format
            )

            # Parse response based on whether structured outputs were used
            if response_format:
                # Structured output returns JSON
                if isinstance(response, str):
                    result = json.loads(response)
                else:
                    result = response

                predicted_category = result.get("category")
                confidence = result.get("confidence", "medium")
            else:
                # Standard output - just category name
                predicted_category = response.strip()
                confidence = None

                # Find matching category
                for cat in categories:
                    if cat["name"].lower() == predicted_category.lower():
                        predicted_category = cat["name"]
                        break

            return {
                "success": True,
                "value": value,
                "predicted_category": predicted_category,
                "confidence": confidence if confidence else "medium",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "value": value,
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
