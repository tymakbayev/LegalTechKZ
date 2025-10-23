"""
Model Pipeline module for orchestrating multiple LLMs.

This module enables sequential processing through different models,
allowing each model to work on tasks they're best suited for.
"""

from typing import Dict, List, Any, Optional, Callable
import logging
from datetime import datetime

from legaltechkz.models.model_router import ModelRouter

logger = logging.getLogger("legaltechkz.model_pipeline")


class PipelineStage:
    """Represents a single stage in the model pipeline."""

    def __init__(
        self,
        name: str,
        stage_type: str,
        prompt_template: Optional[str] = None,
        post_processor: Optional[Callable] = None
    ):
        """
        Initialize a pipeline stage.

        Args:
            name: Stage name for logging.
            stage_type: Type of stage (document_processing, analysis, summarization).
            prompt_template: Template for generating prompts. Use {input} placeholder.
            post_processor: Optional function to process stage output.
        """
        self.name = name
        self.stage_type = stage_type
        self.prompt_template = prompt_template or "{input}"
        self.post_processor = post_processor

    def prepare_prompt(self, input_data: str, **kwargs) -> str:
        """
        Prepare prompt for this stage.

        Args:
            input_data: Input from previous stage or user.
            **kwargs: Additional variables for template.

        Returns:
            Formatted prompt.
        """
        template_vars = {"input": input_data}
        template_vars.update(kwargs)

        try:
            return self.prompt_template.format(**template_vars)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}. Using input as-is.")
            return input_data

    def process_output(self, output: str) -> str:
        """
        Process stage output.

        Args:
            output: Raw output from model.

        Returns:
            Processed output.
        """
        if self.post_processor:
            return self.post_processor(output)
        return output


class ModelPipeline:
    """
    Pipeline for orchestrating multiple LLMs in sequence.

    Example workflow:
    1. User provides full text of law (Gemini processes large document)
    2. Gemini extracts key sections and provisions
    3. Claude analyzes legal implications and reasoning
    4. GPT-4.1 generates concise final response
    """

    def __init__(self, model_router: Optional[ModelRouter] = None):
        """
        Initialize ModelPipeline.

        Args:
            model_router: ModelRouter instance. Creates default if not provided.
        """
        self.model_router = model_router or ModelRouter(enable_auto_selection=True)
        self.stages: List[PipelineStage] = []
        self.execution_history: List[Dict[str, Any]] = []

        logger.info("ModelPipeline initialized")

    def add_stage(
        self,
        name: str,
        stage_type: str,
        prompt_template: Optional[str] = None,
        post_processor: Optional[Callable] = None
    ) -> 'ModelPipeline':
        """
        Add a stage to the pipeline.

        Args:
            name: Stage name.
            stage_type: Stage type (document_processing, analysis, summarization).
            prompt_template: Prompt template with {input} placeholder.
            post_processor: Optional output post-processor.

        Returns:
            Self for method chaining.
        """
        stage = PipelineStage(
            name=name,
            stage_type=stage_type,
            prompt_template=prompt_template,
            post_processor=post_processor
        )
        self.stages.append(stage)

        logger.info(f"Added pipeline stage: {name} ({stage_type})")
        return self

    def execute(
        self,
        initial_input: str,
        template_vars: Optional[Dict[str, Any]] = None,
        return_all_outputs: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the pipeline.

        Args:
            initial_input: Initial input/prompt.
            template_vars: Variables for prompt templates.
            return_all_outputs: If True, return outputs from all stages.

        Returns:
            Execution result with final output and metadata.
        """
        if not self.stages:
            logger.error("Pipeline has no stages configured")
            return {
                "success": False,
                "error": "No stages configured",
                "final_output": None
            }

        logger.info(f"Executing pipeline with {len(self.stages)} stages")

        current_input = initial_input
        stage_outputs = []
        template_vars = template_vars or {}

        execution_record = {
            "start_time": datetime.now().isoformat(),
            "stages": [],
            "success": True
        }

        for i, stage in enumerate(self.stages):
            logger.info(f"Stage {i+1}/{len(self.stages)}: {stage.name}")

            try:
                # Prepare prompt for this stage
                prompt = stage.prepare_prompt(current_input, **template_vars)

                # Select appropriate model for this stage
                model = self.model_router.select_model_for_pipeline_stage(
                    stage=stage.stage_type,
                    previous_output=current_input if i > 0 else None
                )

                # Execute stage
                output = model.generate(prompt)

                # Post-process output
                processed_output = stage.process_output(output)

                # Record stage execution
                stage_record = {
                    "stage_name": stage.name,
                    "stage_type": stage.stage_type,
                    "model": model.model_name,
                    "provider": model.__class__.__name__,
                    "input_length": len(current_input),
                    "output_length": len(processed_output),
                    "success": True
                }

                execution_record["stages"].append(stage_record)
                stage_outputs.append({
                    "stage": stage.name,
                    "output": processed_output
                })

                # Update input for next stage
                current_input = processed_output

                logger.info(
                    f"Stage {stage.name} completed "
                    f"(output: {len(processed_output)} chars)"
                )

            except Exception as e:
                logger.error(f"Error in stage {stage.name}: {e}")
                stage_record = {
                    "stage_name": stage.name,
                    "stage_type": stage.stage_type,
                    "error": str(e),
                    "success": False
                }
                execution_record["stages"].append(stage_record)
                execution_record["success"] = False
                execution_record["error"] = f"Failed at stage {stage.name}: {e}"
                break

        execution_record["end_time"] = datetime.now().isoformat()
        self.execution_history.append(execution_record)

        result = {
            "success": execution_record["success"],
            "final_output": current_input,
            "execution_record": execution_record
        }

        if return_all_outputs:
            result["all_outputs"] = stage_outputs

        if not execution_record["success"]:
            result["error"] = execution_record.get("error")

        return result

    def create_legal_analysis_pipeline(self) -> 'ModelPipeline':
        """
        Create a pre-configured pipeline for legal document analysis.

        Pipeline:
        1. Document Processing (Gemini): Extract and structure content
        2. Legal Analysis (Claude): Analyze provisions and implications
        3. Summary (GPT-4.1): Generate concise response

        Returns:
            Configured pipeline.
        """
        self.stages = []  # Clear existing stages

        # Stage 1: Document Processing with Gemini
        self.add_stage(
            name="Обработка документа",
            stage_type="document_processing",
            prompt_template=(
                "Ты помощник-юрист, специализирующийся на НПА РК.\n\n"
                "Проанализируй следующий текст закона или кодекса и извлеки "
                "ключевые статьи, положения и определения:\n\n{input}\n\n"
                "Структурируй информацию по разделам."
            )
        )

        # Stage 2: Legal Analysis with Claude
        self.add_stage(
            name="Правовой анализ",
            stage_type="analysis",
            prompt_template=(
                "Ты эксперт по праву Казахстана.\n\n"
                "На основе извлечённых данных:\n{input}\n\n"
                "Проведи детальный правовой анализ:\n"
                "1. Определи применимые нормы права\n"
                "2. Проанализируй правовые последствия\n"
                "3. Выяви возможные коллизии или противоречия\n"
                "4. Предложи юридическое заключение"
            )
        )

        # Stage 3: Summarization with GPT-4.1
        self.add_stage(
            name="Формирование ответа",
            stage_type="summarization",
            prompt_template=(
                "На основе правового анализа:\n{input}\n\n"
                "Сформулируй краткий, понятный ответ для пользователя, "
                "сохранив все важные юридические детали."
            )
        )

        logger.info("Legal analysis pipeline configured")
        return self

    def create_document_qa_pipeline(self) -> 'ModelPipeline':
        """
        Create a pipeline for question-answering on large documents.

        Pipeline:
        1. Document Indexing (Gemini): Process and index document
        2. Answer Generation (Claude): Generate detailed answer
        3. Response Formatting (GPT-4.1): Format final response

        Returns:
            Configured pipeline.
        """
        self.stages = []

        self.add_stage(
            name="Индексация документа",
            stage_type="document_processing",
            prompt_template=(
                "Документ для анализа:\n{document}\n\n"
                "Вопрос пользователя: {question}\n\n"
                "Найди и извлеки все релевантные разделы документа, "
                "которые относятся к вопросу."
            )
        )

        self.add_stage(
            name="Генерация ответа",
            stage_type="reasoning",
            prompt_template=(
                "Релевантные разделы:\n{input}\n\n"
                "Вопрос: {question}\n\n"
                "Предоставь детальный, обоснованный ответ на вопрос, "
                "опираясь на найденную информацию."
            )
        )

        self.add_stage(
            name="Форматирование",
            stage_type="quick_response",
            prompt_template=(
                "Ответ для форматирования:\n{input}\n\n"
                "Отформатируй ответ в понятном, структурированном виде."
            )
        )

        logger.info("Document Q&A pipeline configured")
        return self

    def clear_stages(self) -> None:
        """Clear all pipeline stages."""
        self.stages = []
        logger.info("Pipeline stages cleared")

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get pipeline execution history.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of execution records.
        """
        return self.execution_history[-limit:]


# Pre-configured pipeline factory functions

def create_legal_pipeline(model_router: Optional[ModelRouter] = None) -> ModelPipeline:
    """
    Create a legal analysis pipeline.

    Args:
        model_router: Optional ModelRouter instance.

    Returns:
        Configured ModelPipeline.
    """
    pipeline = ModelPipeline(model_router)
    return pipeline.create_legal_analysis_pipeline()


def create_qa_pipeline(model_router: Optional[ModelRouter] = None) -> ModelPipeline:
    """
    Create a document Q&A pipeline.

    Args:
        model_router: Optional ModelRouter instance.

    Returns:
        Configured ModelPipeline.
    """
    pipeline = ModelPipeline(model_router)
    return pipeline.create_document_qa_pipeline()
