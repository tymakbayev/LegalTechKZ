"""
Anthropic Model implementation for the LegalTechKZ framework.
"""

from typing import Dict, List, Any, Optional, Union
import json
import logging
import os

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from legaltechkz.models.base.base_model import BaseModel

class AnthropicModel(BaseModel):
    """
    Anthropic Claude language model implementation.

    Provides integration with Anthropic's Claude API for text generation.
    Supports Claude Sonnet 4.5 and other Claude models.
    """

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-5",
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize an AnthropicModel instance.

        Args:
            model_name: The name of the Claude model to use (e.g., 'claude-sonnet-4-5').
            temperature: Controls randomness in outputs. Lower values are more deterministic.
            max_tokens: Maximum number of tokens to generate.
            api_key: Anthropic API key. If None, it will be read from ANTHROPIC_API_KEY environment variable.
            **kwargs: Additional model-specific parameters.
        """
        super().__init__(model_name, temperature, max_tokens, **kwargs)

        if not ANTHROPIC_AVAILABLE:
            logging.error("Anthropic package not installed. Please install it with 'pip install anthropic'.")
            raise ImportError("Anthropic package not installed")

        # Use provided API key or read from environment
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            logging.error("Anthropic API key not provided and not found in environment.")
            raise ValueError("Anthropic API key required")

        # Initialize client
        self.client = Anthropic(api_key=self.api_key)

        # Set default max_tokens if not provided (Claude requires this parameter)
        if self.max_tokens is None:
            self.max_tokens = 4096

    def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text based on a prompt using Claude.

        Args:
            prompt: The text prompt for generation.
            system_message: Optional system message for the model.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional Anthropic-specific parameters.

        Returns:
            The generated text response.
        """
        # Set parameters
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        try:
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]

            # Make the API call
            response = self.client.messages.create(
                model=self.model_name,
                messages=messages,
                system=system_message if system_message else None,
                temperature=temp,
                max_tokens=tokens,
                **kwargs
            )

            # Extract and return the response text
            return response.content[0].text

        except Exception as e:
            logging.error(f"Error generating with Anthropic: {e}")
            return f"Error: {str(e)}"

    def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text with tool calling capabilities using Claude.

        Args:
            prompt: The text prompt for generation.
            tools: List of tool schemas available for use.
            system_message: Optional system message for the model.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional Anthropic-specific parameters.

        Returns:
            A dictionary with the response and any tool calls.
        """
        # Set parameters
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        # Convert tools to Anthropic format
        anthropic_tools = []
        for tool in tools:
            anthropic_tool = {
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "input_schema": tool.get("parameters", {})
            }
            anthropic_tools.append(anthropic_tool)

        try:
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]

            # Make the API call
            response = self.client.messages.create(
                model=self.model_name,
                messages=messages,
                system=system_message if system_message else None,
                temperature=temp,
                max_tokens=tokens,
                tools=anthropic_tools,
                **kwargs
            )

            # Extract response
            tool_calls = []
            text_content = ""

            for block in response.content:
                if block.type == "text":
                    text_content += block.text
                elif block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "arguments": block.input
                    })

            return {
                "content": text_content if text_content else None,
                "tool_calls": tool_calls
            }

        except Exception as e:
            logging.error(f"Error generating with tools using Anthropic: {e}")
            return {
                "content": f"Error: {str(e)}",
                "tool_calls": []
            }

    def extract_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract structured JSON data based on a prompt using Claude.

        Args:
            prompt: The text prompt for extraction.
            schema: JSON schema describing the expected structure.
            system_message: Optional system message for the model.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional Anthropic-specific parameters.

        Returns:
            The extracted JSON data.
        """
        # Set default system message if not provided
        if not system_message:
            system_message = "Extract the requested information and respond only with a valid JSON object according to the specified schema. Do not include any other text."

        # Set parameters
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        # Create prompt with schema
        full_prompt = f"Schema: {json.dumps(schema)}\n\nPrompt: {prompt}\n\nProvide ONLY valid JSON, no other text."

        try:
            # Make the API call
            response = self.client.messages.create(
                model=self.model_name,
                messages=[{"role": "user", "content": full_prompt}],
                system=system_message,
                temperature=temp,
                max_tokens=tokens,
                **kwargs
            )

            # Extract and parse the response
            content = response.content[0].text

            try:
                # Try to parse JSON directly
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                    return json.loads(json_str)
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                    return json.loads(json_str)
                else:
                    logging.error(f"Failed to parse JSON from response: {content}")
                    return {"error": "Failed to parse JSON response"}

        except Exception as e:
            logging.error(f"Error extracting JSON with Anthropic: {e}")
            return {"error": str(e)}

    def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Generate an embedding vector for the given text.

        Note: Anthropic doesn't provide embedding models directly.
        This method will raise NotImplementedError.
        Consider using OpenAI's embedding models or sentence-transformers instead.

        Args:
            text: The text to embed.
            **kwargs: Additional parameters.

        Returns:
            The embedding vector as a list of floats.

        Raises:
            NotImplementedError: Anthropic doesn't provide embeddings.
        """
        raise NotImplementedError(
            "Anthropic does not provide embedding models. "
            "Use OpenAI's text-embedding-ada-002 or sentence-transformers instead."
        )
