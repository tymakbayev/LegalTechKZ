"""
Google Gemini Model implementation for the LegalTechKZ framework.
"""

from typing import Dict, List, Any, Optional, Union
import json
import logging
import os

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from legaltechkz.models.base.base_model import BaseModel

class GeminiModel(BaseModel):
    """
    Google Gemini language model implementation.

    Provides integration with Google's Gemini API for text generation.
    Supports Gemini 2.5 Flash and other Gemini models.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a GeminiModel instance.

        Args:
            model_name: The name of the Gemini model to use (e.g., 'gemini-2.5-flash').
            temperature: Controls randomness in outputs. Lower values are more deterministic.
            max_tokens: Maximum number of tokens to generate.
            api_key: Google API key. If None, it will be read from GOOGLE_API_KEY environment variable.
            **kwargs: Additional model-specific parameters.
        """
        super().__init__(model_name, temperature, max_tokens, **kwargs)

        if not GEMINI_AVAILABLE:
            logging.error("google-genai package not installed. Please install it with 'pip install google-genai'.")
            raise ImportError("google-genai package not installed")

        # Use provided API key or read from environment
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            logging.error("Google API key not provided and not found in environment.")
            raise ValueError("Google API key required")

        # Initialize client
        self.client = genai.Client(api_key=self.api_key)

        # Store generation config
        self.generation_config = types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            **kwargs
        )

    def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text based on a prompt using Gemini.

        Args:
            prompt: The text prompt for generation.
            system_message: Optional system message for the model.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional Gemini-specific parameters.

        Returns:
            The generated text response.
        """
        # Set parameters
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        # Create generation config
        config = types.GenerateContentConfig(
            temperature=temp,
            max_output_tokens=tokens,
            system_instruction=system_message if system_message else None,
            **kwargs
        )

        try:
            # Make the API call
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Extract and return the response text
            return response.text

        except Exception as e:
            logging.error(f"Error generating with Gemini: {e}")
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
        Generate text with tool calling capabilities using Gemini.

        Args:
            prompt: The text prompt for generation.
            tools: List of tool schemas available for use.
            system_message: Optional system message for the model.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional Gemini-specific parameters.

        Returns:
            A dictionary with the response and any tool calls.
        """
        # Set parameters
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        # Convert tools to Gemini format
        gemini_tools = []
        for tool in tools:
            # Gemini uses function declarations
            function_declaration = types.FunctionDeclaration(
                name=tool.get("name", ""),
                description=tool.get("description", ""),
                parameters=tool.get("parameters", {})
            )
            gemini_tools.append(types.Tool(function_declarations=[function_declaration]))

        # Create generation config
        config = types.GenerateContentConfig(
            temperature=temp,
            max_output_tokens=tokens,
            system_instruction=system_message if system_message else None,
            tools=gemini_tools,
            **kwargs
        )

        try:
            # Make the API call
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Extract response
            tool_calls = []
            text_content = ""

            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    text_content += part.text
                elif hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    tool_calls.append({
                        "id": fc.name,  # Gemini doesn't provide unique IDs
                        "name": fc.name,
                        "arguments": dict(fc.args)
                    })

            return {
                "content": text_content if text_content else None,
                "tool_calls": tool_calls
            }

        except Exception as e:
            logging.error(f"Error generating with tools using Gemini: {e}")
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
        Extract structured JSON data based on a prompt using Gemini.

        Args:
            prompt: The text prompt for extraction.
            schema: JSON schema describing the expected structure.
            system_message: Optional system message for the model.
            temperature: Controls randomness in outputs. Overrides instance value if provided.
            max_tokens: Maximum number of tokens to generate. Overrides instance value if provided.
            **kwargs: Additional Gemini-specific parameters.

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

        # Create generation config with JSON response format
        config = types.GenerateContentConfig(
            temperature=temp,
            max_output_tokens=tokens,
            system_instruction=system_message,
            response_mime_type="application/json",
            **kwargs
        )

        try:
            # Make the API call
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config
            )

            # Extract and parse the response
            content = response.text

            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logging.error(f"Failed to parse JSON from response: {content}")
                return {"error": "Failed to parse JSON response"}

        except Exception as e:
            logging.error(f"Error extracting JSON with Gemini: {e}")
            return {"error": str(e)}

    def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Generate an embedding vector for the given text using Gemini.

        Args:
            text: The text to embed.
            **kwargs: Additional Gemini-specific parameters.

        Returns:
            The embedding vector as a list of floats.
        """
        try:
            # Gemini provides text embeddings through the embed_content method
            response = self.client.models.embed_content(
                model="text-embedding-004",  # Gemini's embedding model
                content=text,
                **kwargs
            )

            return response.embedding

        except Exception as e:
            logging.error(f"Error generating embedding with Gemini: {e}")
            return []
