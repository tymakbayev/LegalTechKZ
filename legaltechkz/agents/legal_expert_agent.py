"""
Специализированный агент для правовой экспертизы НПА РК

Этот агент предназначен для проведения комплексной правовой экспертизы
нормативно-правовых актов Республики Казахстан.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from legaltechkz.core.agent.base_agent import BaseAgent
from legaltechkz.tools.adilet_search import AdiletSearchTool, AdiletDocumentFetcher
from legaltechkz.tools.legal_analysis import (
    LegalConsistencyChecker,
    LegalContradictionDetector,
    LegalReferenceValidator
)

logger = logging.getLogger(__name__)


class LegalExpertAgent(BaseAgent):
    """
    Агент для правовой экспертизы НПА РК

    Функции:
    - Поиск НПА на adilet.zan.kz
    - Проверка консистентности документов
    - Выявление противоречий
    - Валидация ссылок
    - Формирование экспертных заключений
    """

    def __init__(
        self,
        name: str = "legal_expert",
        max_iterations: int = 15,
        **kwargs
    ):
        """
        Инициализация агента правовой экспертизы

        Args:
            name: Имя агента
            max_iterations: Максимальное количество итераций
            **kwargs: Дополнительные параметры
        """
        super().__init__(name=name, max_iterations=max_iterations, **kwargs)

        # Инициализируем инструменты
        self.adilet_search = AdiletSearchTool()
        self.document_fetcher = AdiletDocumentFetcher()
        self.consistency_checker = LegalConsistencyChecker()
        self.contradiction_detector = LegalContradictionDetector()
        self.reference_validator = LegalReferenceValidator()

        # Регистрируем инструменты
        self.tools = {
            "adilet_search": self.adilet_search,
            "fetch_document": self.document_fetcher,
            "check_consistency": self.consistency_checker,
            "detect_contradictions": self.contradiction_detector,
            "validate_references": self.reference_validator
        }

        logger.info(f"Агент правовой экспертизы '{name}' инициализирован с {len(self.tools)} инструментами")

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Выполнить задачу правовой экспертизы

        Args:
            task: Описание задачи
            **kwargs: Дополнительные параметры

        Returns:
            Результаты выполнения задачи
        """
        logger.info(f"Агент '{self.name}' начинает выполнение задачи: {task}")

        try:
            # Анализируем тип задачи
            task_type = self._determine_task_type(task)

            # Выполняем соответствующую задачу
            if task_type == "search":
                result = self._perform_search(task, **kwargs)
            elif task_type == "analysis":
                result = self._perform_analysis(task, **kwargs)
            elif task_type == "comparison":
                result = self._perform_comparison(task, **kwargs)
            elif task_type == "full_examination":
                result = self._perform_full_examination(task, **kwargs)
            else:
                result = self._perform_general_task(task, **kwargs)

            logger.info(f"Агент '{self.name}' завершил выполнение задачи")
            return result

        except Exception as e:
            error_msg = f"Ошибка при выполнении задачи: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "task": task
            }

    def _determine_task_type(self, task: str) -> str:
        """
        Определить тип задачи

        Args:
            task: Описание задачи

        Returns:
            Тип задачи
        """
        task_lower = task.lower()

        if any(word in task_lower for word in ["найти", "найди", "поиск", "ищи"]):
            return "search"
        elif any(word in task_lower for word in ["проанализировать", "анализ", "проверить", "проверка"]):
            return "analysis"
        elif any(word in task_lower for word in ["сравнить", "сравнение", "противоречия"]):
            return "comparison"
        elif any(word in task_lower for word in ["экспертиза", "заключение", "полная проверка"]):
            return "full_examination"
        else:
            return "general"

    def _perform_search(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Выполнить поиск НПА

        Args:
            task: Описание задачи поиска
            **kwargs: Дополнительные параметры

        Returns:
            Результаты поиска
        """
        logger.info("Выполняю поиск НПА на adilet.zan.kz")

        # Извлекаем поисковый запрос из задачи
        query = self._extract_search_query(task)

        # Выполняем поиск
        search_result = self.adilet_search.execute(
            query=query,
            doc_type=kwargs.get("doc_type", "all"),
            year=kwargs.get("year"),
            status=kwargs.get("status", "active")
        )

        return {
            "status": "success",
            "task_type": "search",
            "search_result": search_result,
            "summary": self._generate_search_summary(search_result)
        }

    def _perform_analysis(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Выполнить анализ НПА

        Args:
            task: Описание задачи анализа
            **kwargs: Дополнительные параметры

        Returns:
            Результаты анализа
        """
        logger.info("Выполняю анализ НПА")

        # Получаем документ для анализа
        document = kwargs.get("document")
        if not document:
            # Если документ не предоставлен, ищем его
            query = self._extract_search_query(task)
            search_result = self.adilet_search.execute(query=query)

            if search_result.get("result_count", 0) == 0:
                return {
                    "status": "error",
                    "error": "Документ не найден",
                    "task": task
                }

            # Берем первый результат
            doc_url = search_result["results"][0]["url"]
            doc_result = self.document_fetcher.execute(url=doc_url)
            document = doc_result.get("document")

        # Проверяем консистентность
        consistency_result = self.consistency_checker.execute(
            document_text=document.get("text", ""),
            document_metadata={
                "title": document.get("title"),
                "number": document.get("number"),
                "date": document.get("date")
            }
        )

        return {
            "status": "success",
            "task_type": "analysis",
            "document_info": {
                "title": document.get("title"),
                "number": document.get("number"),
                "date": document.get("date")
            },
            "consistency_result": consistency_result,
            "summary": self._generate_analysis_summary(consistency_result)
        }

    def _perform_comparison(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Выполнить сравнение НПА

        Args:
            task: Описание задачи сравнения
            **kwargs: Дополнительные параметры

        Returns:
            Результаты сравнения
        """
        logger.info("Выполняю сравнение НПА")

        document1 = kwargs.get("document1")
        document2 = kwargs.get("document2")

        if not document1 or not document2:
            return {
                "status": "error",
                "error": "Для сравнения необходимо предоставить два документа",
                "task": task
            }

        # Выявляем противоречия
        contradiction_result = self.contradiction_detector.execute(
            document1=document1,
            document2=document2,
            scope=kwargs.get("scope", "all")
        )

        return {
            "status": "success",
            "task_type": "comparison",
            "contradiction_result": contradiction_result,
            "summary": self._generate_comparison_summary(contradiction_result)
        }

    def _perform_full_examination(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Выполнить полную правовую экспертизу

        Args:
            task: Описание задачи экспертизы
            **kwargs: Дополнительные параметры

        Returns:
            Экспертное заключение
        """
        logger.info("Выполняю полную правовую экспертизу НПА")

        # Этапы экспертизы
        stages = {
            "search": {"status": "pending", "result": None},
            "document_retrieval": {"status": "pending", "result": None},
            "consistency_check": {"status": "pending", "result": None},
            "reference_validation": {"status": "pending", "result": None},
            "related_documents_check": {"status": "pending", "result": None},
            "final_assessment": {"status": "pending", "result": None}
        }

        # Этап 1: Поиск документа
        logger.info("Этап 1: Поиск документа")
        query = self._extract_search_query(task)
        search_result = self.adilet_search.execute(query=query, status="active")
        stages["search"]["status"] = "completed"
        stages["search"]["result"] = search_result

        if search_result.get("result_count", 0) == 0:
            return {
                "status": "error",
                "error": "Документ не найден",
                "stages": stages
            }

        # Этап 2: Получение полного текста
        logger.info("Этап 2: Получение полного текста документа")
        doc_url = search_result["results"][0]["url"]
        doc_result = self.document_fetcher.execute(url=doc_url)
        document = doc_result.get("document")
        stages["document_retrieval"]["status"] = "completed"
        stages["document_retrieval"]["result"] = {
            "title": document.get("title"),
            "url": doc_url
        }

        # Этап 3: Проверка консистентности
        logger.info("Этап 3: Проверка консистентности")
        consistency_result = self.consistency_checker.execute(
            document_text=document.get("text", ""),
            document_metadata={
                "title": document.get("title"),
                "number": document.get("number"),
                "date": document.get("date")
            }
        )
        stages["consistency_check"]["status"] = "completed"
        stages["consistency_check"]["result"] = consistency_result

        # Этап 4: Валидация ссылок
        logger.info("Этап 4: Валидация ссылок на другие НПА")
        references = consistency_result.get("checks", {}).get("references", {}).get("references", [])
        if references:
            reference_texts = [ref["text"] for ref in references]
            validation_result = self.reference_validator.execute(
                references=reference_texts,
                check_online=False  # Можно включить для онлайн проверки
            )
            stages["reference_validation"]["status"] = "completed"
            stages["reference_validation"]["result"] = validation_result
        else:
            stages["reference_validation"]["status"] = "skipped"
            stages["reference_validation"]["result"] = {"message": "Ссылки не найдены"}

        # Этап 5: Проверка связанных документов
        logger.info("Этап 5: Поиск и проверка связанных документов")
        # TODO: Реализовать поиск связанных документов
        stages["related_documents_check"]["status"] = "skipped"
        stages["related_documents_check"]["result"] = {"message": "Проверка связанных документов в разработке"}

        # Этап 6: Формирование итогового заключения
        logger.info("Этап 6: Формирование экспертного заключения")
        final_assessment = self._generate_expert_conclusion(stages, document)
        stages["final_assessment"]["status"] = "completed"
        stages["final_assessment"]["result"] = final_assessment

        return {
            "status": "success",
            "task_type": "full_examination",
            "document_info": {
                "title": document.get("title"),
                "number": document.get("number"),
                "date": document.get("date"),
                "url": doc_url
            },
            "stages": stages,
            "expert_conclusion": final_assessment,
            "timestamp": datetime.now().isoformat()
        }

    def _perform_general_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Выполнить общую задачу

        Args:
            task: Описание задачи
            **kwargs: Дополнительные параметры

        Returns:
            Результаты выполнения
        """
        logger.info("Выполняю общую задачу")

        return {
            "status": "success",
            "task_type": "general",
            "message": "Задача обработана",
            "task": task
        }

    def _extract_search_query(self, task: str) -> str:
        """
        Извлечь поисковый запрос из задачи

        Args:
            task: Описание задачи

        Returns:
            Поисковый запрос
        """
        # Упрощенная реализация - в реальности можно использовать NLP
        import re

        # Ищем фразы в кавычках
        quoted = re.search(r'"([^"]+)"', task)
        if quoted:
            return quoted.group(1)

        # Ищем фразы в одинарных кавычках
        quoted = re.search(r"'([^']+)'", task)
        if quoted:
            return quoted.group(1)

        # Убираем команды и возвращаем остаток
        for keyword in ["найти", "найди", "поиск", "ищи", "проанализировать", "анализ"]:
            task = task.replace(keyword, "").strip()

        return task.strip()

    def _generate_search_summary(self, search_result: Dict[str, Any]) -> str:
        """Генерировать краткое описание результатов поиска"""
        count = search_result.get("result_count", 0)
        if count == 0:
            return "Документы не найдены"
        elif count == 1:
            return f"Найден 1 документ: {search_result['results'][0]['title']}"
        else:
            return f"Найдено {count} документов"

    def _generate_analysis_summary(self, consistency_result: Dict[str, Any]) -> str:
        """Генерировать краткое описание результатов анализа"""
        assessment = consistency_result.get("overall_assessment", {})
        quality = assessment.get("quality", "Неизвестно")
        issues = assessment.get("issues_count", 0)
        warnings = assessment.get("warnings_count", 0)

        summary = f"Качество документа: {quality}. "
        if issues > 0:
            summary += f"Обнаружено критических замечаний: {issues}. "
        if warnings > 0:
            summary += f"Предупреждений: {warnings}."

        return summary

    def _generate_comparison_summary(self, contradiction_result: Dict[str, Any]) -> str:
        """Генерировать краткое описание результатов сравнения"""
        count = contradiction_result.get("contradictions_count", 0)
        if count == 0:
            return "Противоречия не выявлены"
        else:
            return f"Выявлено противоречий: {count}"

    def _generate_expert_conclusion(
        self,
        stages: Dict[str, Any],
        document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Генерировать экспертное заключение

        Args:
            stages: Результаты всех этапов экспертизы
            document: Информация о документе

        Returns:
            Экспертное заключение
        """
        consistency = stages["consistency_check"]["result"]
        assessment = consistency.get("overall_assessment", {})

        conclusion = {
            "document": {
                "title": document.get("title"),
                "number": document.get("number"),
                "date": document.get("date"),
                "status": document.get("status")
            },
            "examination_date": datetime.now().strftime("%d.%m.%Y"),
            "quality_assessment": assessment.get("quality", "Неизвестно"),
            "score": assessment.get("score", 0),
            "ready_for_approval": assessment.get("ready_for_approval", False),
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "detailed_findings": {}
        }

        # Собираем критические замечания
        for issue in consistency.get("issues", []):
            conclusion["critical_issues"].append({
                "type": issue.get("type"),
                "description": issue.get("message"),
                "severity": issue.get("severity", "medium")
            })

        # Собираем предупреждения
        for warning in consistency.get("warnings", []):
            conclusion["warnings"].append({
                "type": warning.get("type"),
                "description": warning.get("message")
            })

        # Собираем рекомендации
        conclusion["recommendations"] = consistency.get("recommendations", [])

        # Детализированные находки
        conclusion["detailed_findings"] = {
            "structure_check": stages["consistency_check"]["result"].get("checks", {}).get("structure", {}),
            "references_check": stages["consistency_check"]["result"].get("checks", {}).get("references", {}),
            "terminology_check": stages["consistency_check"]["result"].get("checks", {}).get("terminology", {})
        }

        # Итоговое заключение
        if assessment.get("ready_for_approval"):
            conclusion["final_verdict"] = "Документ соответствует требованиям и может быть принят"
        elif len(conclusion["critical_issues"]) > 0:
            conclusion["final_verdict"] = "Документ требует доработки перед принятием"
        else:
            conclusion["final_verdict"] = "Документ требует незначительных корректировок"

        return conclusion
