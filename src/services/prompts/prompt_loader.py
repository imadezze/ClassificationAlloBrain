"""Prompt Loader - Loads prompt templates from YAML files"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class PromptLoader:
    """Loads and manages prompt templates from YAML files"""

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize prompt loader

        Args:
            prompts_dir: Directory containing prompt templates (defaults to this file's directory)
        """
        if prompts_dir is None:
            self.prompts_dir = Path(__file__).parent
        else:
            self.prompts_dir = Path(prompts_dir)

        self._cache = {}

    def load_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """
        Load a prompt template by name

        Args:
            prompt_name: Name of the prompt (filename without .yaml extension)

        Returns:
            Dictionary containing prompt template data

        Raises:
            FileNotFoundError: If prompt file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        # Check cache first
        if prompt_name in self._cache:
            return self._cache[prompt_name]

        # Load from file
        prompt_file = self.prompts_dir / f"{prompt_name}.yaml"

        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt template '{prompt_name}' not found at {prompt_file}"
            )

        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_data = yaml.safe_load(f)

        # Cache the loaded prompt
        self._cache[prompt_name] = prompt_data

        return prompt_data

    def get_system_role(self, prompt_name: str) -> str:
        """
        Get system role for a prompt

        Args:
            prompt_name: Name of the prompt

        Returns:
            System role string
        """
        prompt_data = self.load_prompt(prompt_name)
        return prompt_data.get("system_role", "")

    def get_user_template(self, prompt_name: str) -> str:
        """
        Get user message template for a prompt

        Args:
            prompt_name: Name of the prompt

        Returns:
            User template string
        """
        prompt_data = self.load_prompt(prompt_name)
        return prompt_data.get("user_template", "")

    def get_parameters(self, prompt_name: str) -> Dict[str, Any]:
        """
        Get LLM parameters for a prompt (temperature, max_tokens, etc.)

        Args:
            prompt_name: Name of the prompt

        Returns:
            Dictionary of parameters
        """
        prompt_data = self.load_prompt(prompt_name)
        return prompt_data.get("parameters", {})

    def format_prompt(
        self, prompt_name: str, variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format a complete prompt with variables

        Args:
            prompt_name: Name of the prompt
            variables: Dictionary of variables to substitute into template

        Returns:
            Dictionary with 'messages' and 'parameters' keys
        """
        prompt_data = self.load_prompt(prompt_name)

        system_role = prompt_data.get("system_role", "")
        user_template = prompt_data.get("user_template", "")
        parameters = prompt_data.get("parameters", {})

        # Format the user message with variables
        user_message = user_template.format(**variables)

        # Build messages array
        messages = []
        if system_role:
            messages.append({"role": "system", "content": system_role})
        messages.append({"role": "user", "content": user_message})

        return {"messages": messages, "parameters": parameters}

    def get_formatting_rules(self, prompt_name: str) -> Dict[str, str]:
        """
        Get formatting rules for a prompt

        Args:
            prompt_name: Name of the prompt

        Returns:
            Dictionary of formatting rules
        """
        prompt_data = self.load_prompt(prompt_name)
        return prompt_data.get("formatting", {})

    def clear_cache(self):
        """Clear the prompt cache"""
        self._cache.clear()

    def reload_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """
        Reload a prompt from disk (bypass cache)

        Args:
            prompt_name: Name of the prompt

        Returns:
            Dictionary containing prompt template data
        """
        if prompt_name in self._cache:
            del self._cache[prompt_name]
        return self.load_prompt(prompt_name)

    def list_available_prompts(self) -> list[str]:
        """
        List all available prompt templates

        Returns:
            List of prompt names (without .yaml extension)
        """
        yaml_files = self.prompts_dir.glob("*.yaml")
        return [f.stem for f in yaml_files if f.stem != "__init__"]
