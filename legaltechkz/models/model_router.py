"""
Model Router module for dynamic model selection.
"""

from typing import Dict, List, Any, Optional, Union, Type
import logging

from legaltechkz.models.base.base_model import BaseModel
from legaltechkz.models.openai_model import OpenAIModel
from legaltechkz.models.anthropic_model import AnthropicModel
from legaltechkz.models.gemini_model import GeminiModel
from legaltechkz.models.task_classifier import TaskClassifier

class ModelRouter:
    """
    Router for dynamically selecting and managing language models.
    
    Provides functionality for:
    - Registering different model implementations
    - Selecting models based on task requirements
    - Fallback mechanisms for reliability
    """
    
    def __init__(
        self,
        default_model_config: Optional[Dict[str, Any]] = None,
        enable_auto_selection: bool = True
    ):
        """
        Initialize a ModelRouter instance.

        Args:
            default_model_config: Configuration for the default model.
            enable_auto_selection: Enable automatic model selection based on task.
        """
        self.models: Dict[str, BaseModel] = {}
        self.model_classes: Dict[str, Type[BaseModel]] = {
            "openai": OpenAIModel,
            "anthropic": AnthropicModel,
            "gemini": GeminiModel,
            "google": GeminiModel  # Alias for gemini
        }
        self.default_model_config = default_model_config or {
            "provider": "openai",
            "model_name": "gpt-4.1",
            "temperature": 0.0
        }
        self.default_model = None
        self.enable_auto_selection = enable_auto_selection
        self.task_classifier = TaskClassifier(
            default_model=self.default_model_config.get("model_name", "gpt-4.1")
        )

        if enable_auto_selection:
            logging.info("Automatic model selection enabled")
    
    def register_model(self, name: str, model: BaseModel) -> None:
        """
        Register a model instance.
        
        Args:
            name: A unique name for the model.
            model: The model instance to register.
        """
        self.models[name] = model
        logging.info(f"Registered model: {name}")
    
    def register_model_class(self, provider: str, model_class: Type[BaseModel]) -> None:
        """
        Register a model class for a provider.
        
        Args:
            provider: The model provider name.
            model_class: The model class to register.
        """
        self.model_classes[provider] = model_class
        logging.info(f"Registered model class for provider: {provider}")
    
    def get_model(self, name_or_config: Union[str, Dict[str, Any]]) -> BaseModel:
        """
        Get a model instance by name or create one from config.
        
        Args:
            name_or_config: Either a model name or a model configuration dictionary.
            
        Returns:
            A model instance.
        """
        # If it's a string, look up by name
        if isinstance(name_or_config, str):
            # Check registered models
            if name_or_config in self.models:
                return self.models[name_or_config]
            
            # If not found, use default model
            logging.warning(f"Model '{name_or_config}' not found. Using default model.")
            return self.get_default_model()
        
        # If it's a config dict, create a new model
        elif isinstance(name_or_config, dict):
            return self._create_model_from_config(name_or_config)
        
        # Invalid input
        else:
            logging.error(f"Invalid model specification: {name_or_config}")
            return self.get_default_model()
    
    def get_default_model(self) -> BaseModel:
        """
        Get the default model, creating it if necessary.
        
        Returns:
            The default model instance.
        """
        if self.default_model is None:
            self.default_model = self._create_model_from_config(self.default_model_config)
        
        return self.default_model
    
    def select_model_for_task(
        self,
        task: str,
        context: Optional[str] = None,
        requirements: Optional[Dict[str, Any]] = None,
        user_preference: Optional[str] = None
    ) -> BaseModel:
        """
        Select an appropriate model for a given task.

        Uses TaskClassifier to automatically determine the best model based on:
        - Context size (token count)
        - Task type (reasoning, document processing, quick response)
        - User preferences

        Args:
            task: The task description/prompt.
            context: Additional context (e.g., document content).
            requirements: Optional requirements for the model (overrides auto-selection).
            user_preference: User's preferred model name (highest priority).

        Returns:
            The selected model instance.
        """
        # Priority 1: Explicit requirements config
        if requirements:
            logging.info("Using explicit model requirements")
            return self._create_model_from_config(requirements)

        # Priority 2: Auto-selection if enabled
        if self.enable_auto_selection:
            # Use task classifier to determine best model
            classification = self.task_classifier.classify_task(
                prompt=task,
                context=context,
                user_preference=user_preference
            )

            model_name = classification["model"]
            provider = classification["provider"]
            reason = classification["reason"]

            logging.info(
                f"Auto-selected {model_name} ({provider}) - {reason}"
            )

            # Create model config from classification
            model_config = {
                "provider": provider,
                "model_name": model_name,
                "temperature": 0.1
            }

            return self._create_model_from_config(model_config)

        # Priority 3: Default model
        logging.info("Using default model")
        return self.get_default_model()

    def select_model_for_pipeline_stage(
        self,
        stage: str,
        previous_output: Optional[str] = None
    ) -> BaseModel:
        """
        Select model for a specific pipeline stage.

        Pipeline stages:
        - document_processing: Large document ingestion (Gemini 2.5 Flash)
        - analysis: Deep reasoning and analysis (Claude Sonnet 4.5)
        - summarization: Quick response generation (GPT-4.1)

        Args:
            stage: Pipeline stage name.
            previous_output: Output from previous stage.

        Returns:
            Model instance for the stage.
        """
        selection = self.task_classifier.select_for_pipeline(
            stage=stage,
            previous_output=previous_output
        )

        model_config = {
            "provider": selection["provider"],
            "model_name": selection["model"],
            "temperature": 0.1
        }

        logging.info(
            f"Pipeline stage '{stage}' using {selection['model']}"
        )

        return self._create_model_from_config(model_config)
    
    def _create_model_from_config(self, config: Dict[str, Any]) -> BaseModel:
        """
        Create a model instance from a configuration dictionary.
        
        Args:
            config: The model configuration.
            
        Returns:
            A model instance.
        """
        # Get the provider
        provider = config.get("provider", "openai").lower()
        
        # Check if we have a class for this provider
        if provider not in self.model_classes:
            logging.error(f"Unknown model provider: {provider}. Supported providers: {list(self.model_classes.keys())}. Using OpenAI as fallback.")
            provider = "openai"
        
        try:
            # Get the model class
            model_class = self.model_classes[provider]
            
            # Extract kwargs for the model
            kwargs = config.copy()
            kwargs.pop("provider", None)
            
            # Create the model
            return model_class(**kwargs)
            
        except Exception as e:
            logging.error(f"Error creating model for provider {provider}: {e}")

            # Fallback to OpenAI with minimal config
            try:
                return OpenAIModel(model_name="gpt-4.1")
            except Exception as fallback_error:
                raise ValueError(f"Failed to create model for {provider}: {e}. Fallback also failed: {fallback_error}")
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available models.
        
        Returns:
            A list of model information dictionaries.
        """
        models_info = []
        
        # Add instantiated models
        for name, model in self.models.items():
            info = {
                "name": name,
                "type": type(model).__name__,
                "model_name": model.model_name,
                "details": model.get_model_details()
            }
            models_info.append(info)
        
        # Add available providers
        for provider in self.model_classes.keys():
            if provider not in [info["details"].get("provider") for info in models_info]:
                models_info.append({
                    "name": f"{provider}",
                    "type": self.model_classes[provider].__name__,
                    "details": {"provider": provider}
                })
        
        return models_info 