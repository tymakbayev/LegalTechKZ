"""
Task Classifier module for automatic model selection.

This module analyzes tasks and determines the most appropriate LLM model
based on context size, task type, and complexity.
"""

from typing import Dict, Any, Optional, List
import logging
import re

logger = logging.getLogger("legaltechkz.task_classifier")


class TaskClassifier:
    """
    Classifier for determining the best model for a given task.

    Model capabilities (2025):
    - GPT-4.1: 1M tokens context, 32K output - best for quick responses
    - Claude Sonnet 4.5: 200K-1M tokens, 64K output - best for reasoning
    - Gemini 2.5 Flash: 1M tokens, 65K output - best for large documents
    """

    # Model specifications
    MODEL_SPECS = {
        "gpt-4.1": {
            "provider": "openai",
            "context_window": 1_000_000,
            "output_tokens": 32_768,
            "strengths": ["quick_response", "general_queries"],
            "cost_tier": "high"
        },
        "claude-sonnet-4-5": {
            "provider": "anthropic",
            "context_window": 200_000,  # Standard, 1M with beta
            "extended_context": 1_000_000,  # With beta header
            "output_tokens": 64_000,
            "strengths": ["reasoning", "analysis", "code_generation", "planning"],
            "cost_tier": "medium"
        },
        "gemini-2.5-flash": {
            "provider": "gemini",
            "context_window": 1_048_576,
            "output_tokens": 65_535,
            "strengths": ["large_documents", "long_context", "multimodal"],
            "cost_tier": "low"
        }
    }

    # Keywords that indicate task types
    REASONING_KEYWORDS = [
        "анализ", "анализируй", "рассуждение", "объясни", "почему",
        "как", "сравни", "сравнение", "оцени", "критика", "аргумент",
        "логика", "вывод", "заключение", "план", "стратегия",
        "analysis", "reasoning", "explain", "why", "how", "compare",
        "evaluate", "critique", "argument", "logic", "conclusion", "plan"
    ]

    DOCUMENT_KEYWORDS = [
        "закон", "кодекс", "статья", "документ", "текст", "файл",
        "нпа", "нормативный", "правовой акт", "полный текст",
        "law", "code", "article", "document", "text", "file", "full text"
    ]

    QUICK_KEYWORDS = [
        "что такое", "определение", "краткий", "быстро", "скажи",
        "ответь", "да или нет", "simple", "quick", "brief", "short",
        "what is", "definition", "tell me"
    ]

    def __init__(self, default_model: str = "gpt-4.1"):
        """
        Initialize TaskClassifier.

        Args:
            default_model: Default model to use when classification is uncertain.
        """
        self.default_model = default_model
        logger.info("TaskClassifier initialized")

    def classify_task(
        self,
        prompt: str,
        context: Optional[str] = None,
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify a task and recommend the best model.

        Args:
            prompt: The user's prompt/question.
            context: Additional context (e.g., document content).
            user_preference: User's preferred model (overrides classification).

        Returns:
            Dictionary with recommended model and reasoning.
        """
        # If user has preference, use it
        if user_preference:
            logger.info(f"Using user-preferred model: {user_preference}")
            return {
                "model": user_preference,
                "provider": self._get_provider(user_preference),
                "reason": "User preference",
                "task_type": "user_specified"
            }

        # Estimate token count
        total_text = prompt
        if context:
            total_text += "\n" + context

        estimated_tokens = self._estimate_tokens(total_text)

        # Determine task type
        task_type = self._determine_task_type(prompt)

        # Select model based on classification
        selected_model = self._select_model(estimated_tokens, task_type)

        logger.info(
            f"Task classified: type={task_type}, "
            f"tokens≈{estimated_tokens}, model={selected_model}"
        )

        return {
            "model": selected_model,
            "provider": self._get_provider(selected_model),
            "reason": f"Task type: {task_type}, estimated tokens: {estimated_tokens}",
            "task_type": task_type,
            "estimated_tokens": estimated_tokens
        }

    def select_for_pipeline(
        self,
        stage: str,
        previous_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Select model for a specific pipeline stage.

        Pipeline stages:
        1. document_processing: Large document ingestion (Gemini)
        2. analysis: Deep reasoning and analysis (Claude)
        3. summarization: Quick response generation (GPT-4.1)

        Args:
            stage: Pipeline stage name.
            previous_output: Output from previous stage.

        Returns:
            Model configuration for the stage.
        """
        stage_models = {
            "document_processing": "gemini-2.5-flash",
            "analysis": "claude-sonnet-4-5",
            "summarization": "gpt-4.1",
            "reasoning": "claude-sonnet-4-5",
            "quick_response": "gpt-4.1"
        }

        selected_model = stage_models.get(stage, self.default_model)

        logger.info(f"Pipeline stage '{stage}' using model: {selected_model}")

        return {
            "model": selected_model,
            "provider": self._get_provider(selected_model),
            "reason": f"Pipeline stage: {stage}",
            "stage": stage
        }

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses a simple heuristic: ~4 characters per token for English,
        ~2 characters per token for Russian (Cyrillic).

        Args:
            text: Text to estimate.

        Returns:
            Estimated token count.
        """
        if not text:
            return 0

        # Check if text is primarily Cyrillic (Russian)
        cyrillic_chars = len(re.findall(r'[а-яА-ЯёЁ]', text))
        total_chars = len(text)

        if cyrillic_chars / max(total_chars, 1) > 0.3:
            # Russian text: ~2 chars per token
            return len(text) // 2
        else:
            # English text: ~4 chars per token
            return len(text) // 4

    def _determine_task_type(self, prompt: str) -> str:
        """
        Determine the type of task based on keywords.

        Args:
            prompt: User's prompt.

        Returns:
            Task type: 'reasoning', 'large_document', 'quick_response', or 'general'.
        """
        prompt_lower = prompt.lower()

        # Check for large document processing
        if any(keyword in prompt_lower for keyword in self.DOCUMENT_KEYWORDS):
            return "large_document"

        # Check for reasoning tasks
        if any(keyword in prompt_lower for keyword in self.REASONING_KEYWORDS):
            return "reasoning"

        # Check for quick response tasks
        if any(keyword in prompt_lower for keyword in self.QUICK_KEYWORDS):
            return "quick_response"

        # Default
        return "general"

    def _select_model(self, estimated_tokens: int, task_type: str) -> str:
        """
        Select the best model based on tokens and task type.

        Args:
            estimated_tokens: Estimated token count.
            task_type: Type of task.

        Returns:
            Selected model name.
        """
        # Very large context (> 150K tokens) -> Gemini
        # Gemini has the largest practical context window
        if estimated_tokens > 150_000:
            logger.debug(f"Large context ({estimated_tokens} tokens) -> Gemini")
            return "gemini-2.5-flash"

        # Task type-based selection for medium contexts
        if task_type == "large_document":
            # User explicitly mentions documents/laws
            return "gemini-2.5-flash"

        elif task_type == "reasoning":
            # Complex reasoning, analysis, planning
            return "claude-sonnet-4-5"

        elif task_type == "quick_response":
            # Simple, quick queries
            return "gpt-4.1"

        else:
            # General tasks - use default (GPT-4.1)
            return self.default_model

    def _get_provider(self, model_name: str) -> str:
        """
        Get provider name for a model.

        Args:
            model_name: Model name.

        Returns:
            Provider name.
        """
        for model, specs in self.MODEL_SPECS.items():
            if model in model_name:
                return specs["provider"]

        # Default to openai
        return "openai"

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a model.

        Args:
            model_name: Model name.

        Returns:
            Model specifications.
        """
        for model, specs in self.MODEL_SPECS.items():
            if model in model_name:
                return specs.copy()

        return {}

    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available models with their capabilities.

        Returns:
            List of model specifications.
        """
        return [
            {"name": name, **specs}
            for name, specs in self.MODEL_SPECS.items()
        ]
