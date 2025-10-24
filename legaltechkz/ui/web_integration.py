"""
Модуль интеграции Web-интерфейса с системой правовой экспертизы.

Обеспечивает связь между Streamlit UI и backend логикой:
- Запуск pipeline экспертизы
- Управление состоянием анализа
- Форматирование результатов для UI
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json

from legaltechkz.utils.logging_config import setup_logging, create_session_log_dir
from legaltechkz.expertise.document_parser import NPADocumentParser, DocumentFragment
from legaltechkz.expertise.completeness_validator import CompletenessValidator
from legaltechkz.expertise.expert_agents import (
    RelevanceFilterAgent,
    ConstitutionalityFilterAgent,
    SystemIntegrationFilterAgent,
    LegalTechnicalExpertAgent,
    AntiCorruptionExpertAgent,
    GenderExpertAgent
)
from legaltechkz.models.model_router import ModelRouter


@dataclass
class ExpertiseProgress:
    """Состояние прогресса экспертизы."""
    current_stage: int
    total_stages: int
    stage_name: str
    articles_processed: int
    total_articles: int
    is_complete: bool
    errors: List[str]


@dataclass
class StageResult:
    """Результат одного этапа экспертизы."""
    stage_name: str
    stage_number: int
    status: str  # "success", "warning", "error"
    articles_analyzed: int
    issues_found: int
    recommendations: List[str]
    detailed_results: Dict[str, Any]
    processing_time: float


class WebExpertiseController:
    """
    Контроллер для управления процессом экспертизы из web-интерфейса.
    """

    def __init__(self):
        """Инициализация контроллера."""
        # Инициализируем логирование в папку ./logs
        session_name = f"expertise_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        setup_logging(log_level="INFO", session_name=session_name)

        self.parser = NPADocumentParser()
        self.model_router = ModelRouter(enable_auto_selection=True)
        self.validator: Optional[CompletenessValidator] = None
        self.fragments: List[DocumentFragment] = []
        self.current_log_file = f"logs/{session_name}.log"

        self.logger = logging.getLogger(__name__)
        self.logger.info("WebExpertiseController инициализирован")
        self.logger.info(f"Логи сохраняются в: {self.current_log_file}")

    def parse_document(self, document_text: str) -> Dict[str, Any]:
        """
        Парсинг документа на структурные элементы.

        Args:
            document_text: Полный текст НПА

        Returns:
            Информация о структуре документа
        """
        try:
            self.fragments = self.parser.parse(document_text)

            if not self.fragments:
                return {
                    "success": False,
                    "error": "Не удалось распарсить документ. Проверьте формат текста.",
                    "fragments_count": 0
                }

            # Создать валидатор полноты
            self.validator = CompletenessValidator(self.fragments)

            # Подсчет элементов
            articles = [f for f in self.fragments if f.type == "article"]
            chapters = [f for f in self.fragments if f.type == "chapter"]
            paragraphs = [f for f in self.fragments if f.type == "paragraph"]

            return {
                "success": True,
                "fragments_count": len(self.fragments),
                "articles_count": len(articles),
                "chapters_count": len(chapters),
                "paragraphs_count": len(paragraphs),
                "table_of_contents": self.validator.generate_checklist_text(),
                "fragments": self.fragments
            }

        except Exception as e:
            self.logger.error(f"Ошибка парсинга документа: {e}")
            return {
                "success": False,
                "error": str(e),
                "fragments_count": 0
            }

    def run_expertise_pipeline(
        self,
        document_text: str,
        document_metadata: Dict[str, str],
        stages: Dict[str, bool],
        options: Dict[str, bool],
        progress_callback: Optional[Callable[[ExpertiseProgress], None]] = None
    ) -> Dict[str, Any]:
        """
        Запуск полного pipeline правовой экспертизы.

        Args:
            document_text: Текст НПА
            document_metadata: Метаданные документа
            stages: Какие этапы выполнять
            options: Опции выполнения (caching, thinking, etc.)
            progress_callback: Callback для обновления прогресса

        Returns:
            Результаты экспертизы
        """
        start_time = datetime.now()

        try:
            # Шаг 1: Парсинг документа
            parse_result = self.parse_document(document_text)

            if not parse_result["success"]:
                return {
                    "success": False,
                    "error": parse_result["error"],
                    "stage": "parsing"
                }

            # Активные этапы
            stage_config = [
                ("relevance", "Фильтр Релевантности"),
                ("constitutionality", "Фильтр Конституционности"),
                ("system_integration", "Фильтр Системной Интеграции"),
                ("legal_technical", "Юридико-техническая экспертиза"),
                ("anti_corruption", "Антикоррупционная экспертиза"),
                ("gender", "Гендерная экспертиза")
            ]

            active_stages = [(k, n) for k, n in stage_config if stages.get(k, False)]
            total_stages = len(active_stages)

            if total_stages == 0:
                return {
                    "success": False,
                    "error": "Не выбрано ни одного этапа экспертизы",
                    "stage": "configuration"
                }

            # Результаты этапов
            stage_results: List[StageResult] = []

            # Выполнение этапов
            for i, (stage_key, stage_name) in enumerate(active_stages, 1):
                stage_start = datetime.now()

                # Обновление прогресса
                if progress_callback:
                    progress = ExpertiseProgress(
                        current_stage=i,
                        total_stages=total_stages,
                        stage_name=stage_name,
                        articles_processed=0,
                        total_articles=parse_result["articles_count"],
                        is_complete=False,
                        errors=[]
                    )
                    progress_callback(progress)

                # Выполнение этапа
                stage_result = self._execute_stage(
                    stage_key=stage_key,
                    stage_name=stage_name,
                    stage_number=i,
                    options=options
                )

                stage_duration = (datetime.now() - stage_start).total_seconds()
                stage_result.processing_time = stage_duration

                stage_results.append(stage_result)

            # Финальная валидация полноты
            completeness_report = self.validator.get_completion_report()

            # Общие метрики
            total_issues = sum(r.issues_found for r in stage_results)
            all_successful = all(r.status == "success" for r in stage_results)

            # Оценка качества (упрощенная логика)
            quality_score = 100
            if total_issues > 0:
                quality_score -= min(total_issues * 5, 30)
            if not completeness_report["is_complete"]:
                quality_score -= 20

            quality_score = max(quality_score, 0)

            # Итоговый вердикт
            if quality_score >= 90 and all_successful:
                verdict = "Документ готов к принятию"
                verdict_status = "success"
            elif quality_score >= 70:
                verdict = "Документ требует незначительных доработок"
                verdict_status = "warning"
            else:
                verdict = "Документ требует существенных доработок"
                verdict_status = "error"

            # Финальный результат
            total_duration = (datetime.now() - start_time).total_seconds()

            return {
                "success": True,
                "document": document_metadata,
                "parsing": parse_result,
                "stages_completed": len(stage_results),
                "stage_results": [self._stage_result_to_dict(r) for r in stage_results],
                "completeness": completeness_report,
                "overall": {
                    "quality_score": quality_score,
                    "total_issues": total_issues,
                    "verdict": verdict,
                    "verdict_status": verdict_status,
                    "ready_for_approval": quality_score >= 80 and all_successful,
                    "processing_time": total_duration
                },
                "log_file": self.current_log_file,  # Путь к файлу логов
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Ошибка выполнения экспертизы: {e}")
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "stage": "execution"
            }

    def _execute_stage(
        self,
        stage_key: str,
        stage_name: str,
        stage_number: int,
        options: Dict[str, bool]
    ) -> StageResult:
        """
        Выполнение одного этапа экспертизы с реальными агентами.

        Args:
            stage_key: Ключ этапа
            stage_name: Название этапа
            stage_number: Номер этапа
            options: Опции выполнения

        Returns:
            Результат этапа
        """
        try:
            articles = [f for f in self.fragments if f.type == "article"]

            if not articles:
                self.logger.warning(f"Нет статей для анализа на этапе '{stage_name}'")
                return StageResult(
                    stage_name=stage_name,
                    stage_number=stage_number,
                    status="warning",
                    articles_analyzed=0,
                    issues_found=0,
                    recommendations=["Статьи для анализа не найдены"],
                    detailed_results={},
                    processing_time=0.0
                )

            # Генерация чеклиста
            checklist = self.validator.generate_checklist_text()

            # Оценка размера контента для выбора модели
            total_chars = sum(len(article.text) for article in articles)
            estimated_tokens = total_chars // 2  # Для русского текста ~2 символа на токен

            # Выбор модели: Gemini для больших объемов, Claude для средних/малых
            # Как указал пользователь: Gemini берет большие тексты, Claude "раскладывает по полочкам"
            if estimated_tokens > 50_000:
                # Большой объем (>50K токенов) - используем Gemini
                pipeline_stage = "document_processing"
                self.logger.info(f"Большой объем данных ({estimated_tokens} токенов) - используем Gemini для начальной обработки")
            else:
                # Средний/малый объем - используем Claude для детального анализа
                pipeline_stage = "analysis"
                self.logger.info(f"Умеренный объем данных ({estimated_tokens} токенов) - используем Claude для детального анализа")

            model = self.model_router.select_model_for_pipeline_stage(pipeline_stage)

            # Создание агента в зависимости от этапа
            agent_map = {
                "relevance": RelevanceFilterAgent,
                "constitutionality": ConstitutionalityFilterAgent,
                "system_integration": SystemIntegrationFilterAgent,
                "legal_technical": LegalTechnicalExpertAgent,
                "anti_corruption": AntiCorruptionExpertAgent,
                "gender": GenderExpertAgent
            }

            agent_class = agent_map.get(stage_key)
            if not agent_class:
                raise ValueError(f"Неизвестный тип этапа: {stage_key}")

            # Инициализация агента
            agent = agent_class(model)

            self.logger.info(f"Запуск этапа '{stage_name}' с агентом {agent.agent_name}")
            self.logger.info(f"Модель: {model.model_name}, Статей для анализа: {len(articles)}")

            # Выполнение batch-анализа
            results = agent.analyze_batch(articles, checklist)

            # Обработка результатов
            successful_analyses = [r for r in results if r.get('success', False)]
            failed_analyses = [r for r in results if not r.get('success', False)]

            # Помечаем проанализированные статьи в валидаторе
            for result in successful_analyses:
                self.validator.mark_analyzed(
                    result['fragment_number'],
                    result
                )

            # Извлекаем рекомендации и проблемы из анализа
            recommendations = []
            issues_count = 0

            for result in successful_analyses:
                analysis_text = result.get('analysis', '')

                # Простой подсчет проблем/рекомендаций (можно улучшить парсингом)
                if 'проблем' in analysis_text.lower() or 'issue' in analysis_text.lower():
                    issues_count += 1

                # Извлекаем первые 200 символов как рекомендацию
                if analysis_text:
                    summary = analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text
                    recommendations.append(f"Статья {result['fragment_number']}: {summary}")

            # Если анализов не было, добавляем общую рекомендацию
            if not recommendations:
                recommendations.append(f"Проанализировано {len(successful_analyses)} статей")

            # Определение статуса этапа
            if len(failed_analyses) > 0:
                status = "warning"
            elif issues_count > 0:
                status = "warning"
            else:
                status = "success"

            self.logger.info(f"Этап '{stage_name}' завершен: {len(successful_analyses)}/{len(articles)} успешно")

            return StageResult(
                stage_name=stage_name,
                stage_number=stage_number,
                status=status,
                articles_analyzed=len(successful_analyses),
                issues_found=issues_count,
                recommendations=recommendations[:5],  # Первые 5 рекомендаций
                detailed_results={
                    "stage_key": stage_key,
                    "options_used": options,
                    "successful_count": len(successful_analyses),
                    "failed_count": len(failed_analyses),
                    "all_results": results  # Полные результаты анализа
                },
                processing_time=0.0  # Будет установлено позже
            )

        except Exception as e:
            self.logger.error(f"Ошибка выполнения этапа {stage_name}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

            return StageResult(
                stage_name=stage_name,
                stage_number=stage_number,
                status="error",
                articles_analyzed=0,
                issues_found=0,
                recommendations=[f"Ошибка: {str(e)}"],
                detailed_results={"error": str(e), "traceback": traceback.format_exc()},
                processing_time=0.0
            )

    def _stage_result_to_dict(self, result: StageResult) -> Dict[str, Any]:
        """Конвертация результата этапа в словарь."""
        return {
            "stage_name": result.stage_name,
            "stage_number": result.stage_number,
            "status": result.status,
            "articles_analyzed": result.articles_analyzed,
            "issues_found": result.issues_found,
            "recommendations": result.recommendations,
            "detailed_results": result.detailed_results,
            "processing_time": result.processing_time
        }

    def export_results_json(self, results: Dict[str, Any]) -> str:
        """
        Экспорт результатов в JSON.

        Args:
            results: Результаты экспертизы

        Returns:
            JSON строка
        """
        return json.dumps(results, ensure_ascii=False, indent=2)

    def export_results_text(self, results: Dict[str, Any]) -> str:
        """
        Экспорт результатов в текстовый формат.

        Args:
            results: Результаты экспертизы

        Returns:
            Текстовое представление отчета
        """
        if not results.get("success"):
            return f"Ошибка: {results.get('error')}"

        lines = []
        lines.append("=" * 80)
        lines.append("ОТЧЕТ О ПРАВОВОЙ ЭКСПЕРТИЗЕ НПА РК")
        lines.append("=" * 80)
        lines.append("")

        # Документ
        doc = results.get("document", {})
        lines.append(f"Документ: {doc.get('title', 'Без названия')}")
        lines.append(f"Номер: {doc.get('number', 'Не указан')}")
        lines.append(f"Дата анализа: {results.get('timestamp', '')}")
        lines.append("")

        # Структура
        parsing = results.get("parsing", {})
        lines.append("СТРУКТУРА ДОКУМЕНТА:")
        lines.append(f"  Всего элементов: {parsing.get('fragments_count', 0)}")
        lines.append(f"  Статей: {parsing.get('articles_count', 0)}")
        lines.append(f"  Глав: {parsing.get('chapters_count', 0)}")
        lines.append("")

        # Этапы
        lines.append("РЕЗУЛЬТАТЫ ЭТАПОВ ЭКСПЕРТИЗЫ:")
        lines.append("-" * 80)

        for stage in results.get("stage_results", []):
            icon = "✅" if stage["status"] == "success" else "⚠️"
            lines.append(f"{icon} Этап {stage['stage_number']}: {stage['stage_name']}")
            lines.append(f"   Проанализировано статей: {stage['articles_analyzed']}")
            lines.append(f"   Найдено проблем: {stage['issues_found']}")

            if stage["recommendations"]:
                lines.append("   Рекомендации:")
                for rec in stage["recommendations"]:
                    lines.append(f"     - {rec}")

            lines.append(f"   Время обработки: {stage['processing_time']:.2f} сек")
            lines.append("")

        # Полнота
        completeness = results.get("completeness", {})
        lines.append("ПОЛНОТА АНАЛИЗА:")
        lines.append(f"  Проанализировано статей: {completeness.get('analyzed_articles', 0)}/{completeness.get('total_articles', 0)}")
        lines.append(f"  Процент полноты: {completeness.get('completion_rate', 0):.1f}%")
        lines.append("")

        # Итого
        overall = results.get("overall", {})
        lines.append("=" * 80)
        lines.append("ИТОГОВОЕ ЗАКЛЮЧЕНИЕ")
        lines.append("=" * 80)
        lines.append(f"Общая оценка: {overall.get('quality_score', 0)}/100")
        lines.append(f"Всего проблем: {overall.get('total_issues', 0)}")
        lines.append(f"Вердикт: {overall.get('verdict', '')}")
        lines.append(f"Готов к принятию: {'Да' if overall.get('ready_for_approval') else 'Нет'}")
        lines.append(f"Общее время обработки: {overall.get('processing_time', 0):.2f} сек")
        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)


# Singleton instance для использования в web-интерфейсе
_controller_instance: Optional[WebExpertiseController] = None


def get_controller() -> WebExpertiseController:
    """
    Получить singleton instance контроллера.

    Returns:
        Instance WebExpertiseController
    """
    global _controller_instance

    if _controller_instance is None:
        _controller_instance = WebExpertiseController()

    return _controller_instance
