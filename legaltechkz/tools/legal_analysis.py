"""
Инструменты для правовой экспертизы НПА РК

Этот модуль содержит инструменты для анализа нормативно-правовых актов:
- Проверка консистентности
- Выявление противоречий
- Анализ ссылок на другие НПА
- Проверка актуальности
- Структурный анализ
"""

import logging
import re
from typing import Dict, Any, Union, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict

from legaltechkz.tools.base.tool import BaseTool
from legaltechkz.tools.base.tool_result import ToolResult

logger = logging.getLogger(__name__)


class LegalConsistencyChecker(BaseTool):
    """
    Инструмент для проверки консистентности НПА

    Проверяет:
    - Ссылки на другие НПА (валидность)
    - Противоречия между документами
    - Актуальность норм
    - Структурную корректность
    """

    name = "legal_consistency_check"
    description = "Проверка консистентности и актуальности НПА"
    parameters = {
        "type": "object",
        "properties": {
            "document_text": {
                "type": "string",
                "description": "Текст анализируемого НПА"
            },
            "document_metadata": {
                "type": "object",
                "description": "Метаданные документа (тип, номер, дата)"
            },
            "check_references": {
                "type": "boolean",
                "description": "Проверять ли ссылки на другие НПА"
            },
            "check_structure": {
                "type": "boolean",
                "description": "Проверять ли структуру документа"
            }
        },
        "required": ["document_text"]
    }

    def execute(
        self,
        document_text: str,
        document_metadata: Optional[Dict[str, Any]] = None,
        check_references: bool = True,
        check_structure: bool = True,
        **kwargs
    ) -> Union[Dict[str, Any], ToolResult]:
        """
        Выполнить проверку консистентности документа

        Args:
            document_text: Текст документа
            document_metadata: Метаданные документа
            check_references: Проверять ссылки
            check_structure: Проверять структуру
            **kwargs: Дополнительные параметры

        Returns:
            Результаты проверки
        """
        try:
            logger.info("Начало проверки консистентности НПА")

            results = {
                "status": "success",
                "document_info": document_metadata or {},
                "checks": {},
                "issues": [],
                "warnings": [],
                "recommendations": []
            }

            # Проверка ссылок на другие НПА
            if check_references:
                logger.info("Проверка ссылок на другие НПА")
                reference_check = self._check_references(document_text)
                results["checks"]["references"] = reference_check
                results["issues"].extend(reference_check.get("issues", []))
                results["warnings"].extend(reference_check.get("warnings", []))

            # Проверка структуры документа
            if check_structure:
                logger.info("Проверка структуры документа")
                structure_check = self._check_structure(document_text)
                results["checks"]["structure"] = structure_check
                results["issues"].extend(structure_check.get("issues", []))
                results["warnings"].extend(structure_check.get("warnings", []))

            # Проверка терминологии
            terminology_check = self._check_terminology(document_text)
            results["checks"]["terminology"] = terminology_check
            results["warnings"].extend(terminology_check.get("warnings", []))

            # Формирование рекомендаций
            results["recommendations"] = self._generate_recommendations(results)

            # Общая оценка
            results["overall_assessment"] = self._calculate_assessment(results)

            logger.info(f"Проверка завершена. Найдено проблем: {len(results['issues'])}, "
                       f"предупреждений: {len(results['warnings'])}")

            return results

        except Exception as e:
            error_msg = f"Ошибка при проверке консистентности: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }

    def _check_references(self, text: str) -> Dict[str, Any]:
        """
        Проверить ссылки на другие НПА

        Args:
            text: Текст документа

        Returns:
            Результаты проверки ссылок
        """
        # Паттерны для поиска ссылок на НПА
        patterns = {
            "law": r'Закон(?:а|у|е)?\s+Республики\s+Казахстан\s+(?:от\s+)?(\d{1,2}\s+\w+\s+\d{4}\s+года?)?\s*№?\s*(\d+-[IVX]+)',
            "code": r'(Гражданский|Уголовный|Административный|Налоговый|Трудовой)\s+кодекс(?:а|у|е)?',
            "decree": r'Указ(?:а|у|е)?\s+Президента\s+(?:РК|Республики\s+Казахстан)\s+(?:от\s+)?(\d{1,2}\s+\w+\s+\d{4}\s+года?)?\s*№?\s*(\d+)',
            "resolution": r'Постановлени(?:е|я|ю)\s+Правительства\s+(?:РК|Республики\s+Казахстан)\s+(?:от\s+)?(\d{1,2}\s+\w+\s+\d{4}\s+года?)?\s*№?\s*(\d+)'
        }

        references = []
        issues = []
        warnings = []

        for ref_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                reference = {
                    "type": ref_type,
                    "text": match.group(0),
                    "position": match.start()
                }
                references.append(reference)

                # Проверяем полноту ссылки
                if not self._is_reference_complete(match.group(0)):
                    warnings.append({
                        "type": "incomplete_reference",
                        "message": f"Неполная ссылка на {ref_type}: {match.group(0)}",
                        "position": match.start()
                    })

        return {
            "total_references": len(references),
            "references": references,
            "issues": issues,
            "warnings": warnings
        }

    def _is_reference_complete(self, reference: str) -> bool:
        """Проверить, полная ли ссылка на НПА"""
        # Полная ссылка должна содержать дату и номер
        has_date = bool(re.search(r'\d{1,2}\s+\w+\s+\d{4}', reference))
        has_number = bool(re.search(r'№?\s*\d+', reference))
        return has_date or has_number

    def _check_structure(self, text: str) -> Dict[str, Any]:
        """
        Проверить структуру документа

        Args:
            text: Текст документа

        Returns:
            Результаты проверки структуры
        """
        issues = []
        warnings = []
        structure = {
            "has_chapters": False,
            "has_articles": False,
            "has_paragraphs": False,
            "chapters": [],
            "articles": [],
            "sections": []
        }

        # Поиск глав
        chapters = re.finditer(r'(?:Глава|ГЛАВА)\s+(\d+|[IVX]+)\.?\s+(.+?)(?:\n|$)', text)
        for match in chapters:
            structure["has_chapters"] = True
            structure["chapters"].append({
                "number": match.group(1),
                "title": match.group(2).strip(),
                "position": match.start()
            })

        # Поиск статей
        articles = re.finditer(r'(?:Статья|СТАТЬЯ)\s+(\d+)\.?\s+(.+?)(?:\n|$)', text)
        for match in articles:
            structure["has_articles"] = True
            structure["articles"].append({
                "number": match.group(1),
                "title": match.group(2).strip(),
                "position": match.start()
            })

        # Поиск параграфов
        paragraphs = re.finditer(r'(?:Параграф|ПАРАГРАФ)\s+(\d+)\.?\s+(.+?)(?:\n|$)', text)
        for match in paragraphs:
            structure["has_paragraphs"] = True
            structure["sections"].append({
                "number": match.group(1),
                "title": match.group(2).strip(),
                "position": match.start()
            })

        # Проверяем последовательность нумерации статей
        if structure["articles"]:
            article_numbers = [int(a["number"]) for a in structure["articles"]]
            for i in range(len(article_numbers) - 1):
                if article_numbers[i + 1] != article_numbers[i] + 1:
                    issues.append({
                        "type": "article_numbering",
                        "message": f"Нарушение последовательности нумерации статей: {article_numbers[i]} -> {article_numbers[i+1]}",
                        "severity": "high"
                    })

        # Проверяем наличие обязательных элементов
        if not structure["has_articles"] and len(text) > 1000:
            warnings.append({
                "type": "missing_articles",
                "message": "Документ не содержит статей, хотя объем текста значительный"
            })

        return {
            "structure": structure,
            "issues": issues,
            "warnings": warnings
        }

    def _check_terminology(self, text: str) -> Dict[str, Any]:
        """
        Проверить терминологию

        Args:
            text: Текст документа

        Returns:
            Результаты проверки терминологии
        """
        warnings = []

        # Словарь устаревших терминов
        deprecated_terms = {
            "прокурор": "прокуратура",  # Пример
            # Добавьте актуальные устаревшие термины
        }

        # Поиск устаревших терминов
        for old_term, new_term in deprecated_terms.items():
            if old_term.lower() in text.lower():
                warnings.append({
                    "type": "deprecated_terminology",
                    "message": f"Используется устаревший термин '{old_term}', рекомендуется '{new_term}'"
                })

        return {
            "warnings": warnings
        }

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Генерировать рекомендации на основе результатов проверки"""
        recommendations = []

        # Рекомендации по ссылкам
        ref_check = results.get("checks", {}).get("references", {})
        if ref_check.get("warnings"):
            recommendations.append(
                "Рекомендуется дополнить ссылки на НПА полной информацией (дата и номер документа)"
            )

        # Рекомендации по структуре
        struct_check = results.get("checks", {}).get("structure", {})
        if struct_check.get("issues"):
            recommendations.append(
                "Необходимо исправить нарушения структуры документа"
            )

        # Общие рекомендации
        if len(results.get("issues", [])) > 0:
            recommendations.append(
                "Требуется устранение критических замечаний перед принятием документа"
            )

        return recommendations

    def _calculate_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Рассчитать общую оценку документа"""
        issues_count = len(results.get("issues", []))
        warnings_count = len(results.get("warnings", []))

        # Определяем уровень качества
        if issues_count == 0 and warnings_count == 0:
            quality = "Отлично"
            score = 100
        elif issues_count == 0 and warnings_count <= 3:
            quality = "Хорошо"
            score = 85
        elif issues_count <= 2 and warnings_count <= 5:
            quality = "Удовлетворительно"
            score = 70
        else:
            quality = "Требует доработки"
            score = 50

        return {
            "quality": quality,
            "score": score,
            "issues_count": issues_count,
            "warnings_count": warnings_count,
            "ready_for_approval": issues_count == 0
        }


class LegalContradictionDetector(BaseTool):
    """
    Инструмент для выявления противоречий между НПА
    """

    name = "legal_contradiction_detector"
    description = "Выявление противоречий между нормативно-правовыми актами"
    parameters = {
        "type": "object",
        "properties": {
            "document1": {
                "type": "object",
                "description": "Первый документ для сравнения"
            },
            "document2": {
                "type": "object",
                "description": "Второй документ для сравнения"
            },
            "scope": {
                "type": "string",
                "description": "Область проверки: all, definitions, norms, procedures"
            }
        },
        "required": ["document1", "document2"]
    }

    def execute(
        self,
        document1: Dict[str, Any],
        document2: Dict[str, Any],
        scope: str = "all",
        **kwargs
    ) -> Union[Dict[str, Any], ToolResult]:
        """
        Выявить противоречия между документами

        Args:
            document1: Первый документ
            document2: Второй документ
            scope: Область проверки
            **kwargs: Дополнительные параметры

        Returns:
            Выявленные противоречия
        """
        try:
            logger.info(f"Проверка противоречий между документами")

            contradictions = []
            warnings = []

            # Извлекаем тексты
            text1 = document1.get("text", "")
            text2 = document2.get("text", "")

            # Проверяем определения
            if scope in ["all", "definitions"]:
                def_contradictions = self._check_definitions(text1, text2)
                contradictions.extend(def_contradictions)

            # Проверяем нормы
            if scope in ["all", "norms"]:
                norm_contradictions = self._check_norms(text1, text2)
                contradictions.extend(norm_contradictions)

            # Проверяем процедуры
            if scope in ["all", "procedures"]:
                proc_contradictions = self._check_procedures(text1, text2)
                contradictions.extend(proc_contradictions)

            return {
                "status": "success",
                "document1_info": {
                    "title": document1.get("title"),
                    "number": document1.get("number"),
                    "date": document1.get("date")
                },
                "document2_info": {
                    "title": document2.get("title"),
                    "number": document2.get("number"),
                    "date": document2.get("date")
                },
                "contradictions": contradictions,
                "contradictions_count": len(contradictions),
                "warnings": warnings,
                "has_conflicts": len(contradictions) > 0
            }

        except Exception as e:
            error_msg = f"Ошибка при выявлении противоречий: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }

    def _check_definitions(self, text1: str, text2: str) -> List[Dict[str, Any]]:
        """Проверить противоречия в определениях"""
        # Упрощенная реализация
        contradictions = []

        # Извлекаем определения из обоих документов
        definitions1 = self._extract_definitions(text1)
        definitions2 = self._extract_definitions(text2)

        # Ищем одинаковые термины с разными определениями
        common_terms = set(definitions1.keys()) & set(definitions2.keys())

        for term in common_terms:
            if definitions1[term] != definitions2[term]:
                contradictions.append({
                    "type": "definition_conflict",
                    "term": term,
                    "definition1": definitions1[term],
                    "definition2": definitions2[term],
                    "severity": "medium"
                })

        return contradictions

    def _extract_definitions(self, text: str) -> Dict[str, str]:
        """Извлечь определения из текста"""
        definitions = {}

        # Поиск определений по паттернам
        # "Термин - это определение"
        # "Под термином понимается определение"
        patterns = [
            r'([А-ЯЁ][а-яё\s]+)\s*-\s*(?:это\s+)?(.+?)(?:\.|;|\n)',
            r'(?:Под|под)\s+([а-яё\s]+)\s+понимается\s+(.+?)(?:\.|;|\n)'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                definitions[term.lower()] = definition

        return definitions

    def _check_norms(self, text1: str, text2: str) -> List[Dict[str, Any]]:
        """Проверить противоречия в нормах"""
        # Упрощенная реализация
        return []

    def _check_procedures(self, text1: str, text2: str) -> List[Dict[str, Any]]:
        """Проверить противоречия в процедурах"""
        # Упрощенная реализация
        return []


class LegalReferenceValidator(BaseTool):
    """
    Инструмент для валидации ссылок на НПА
    """

    name = "legal_reference_validator"
    description = "Проверка валидности ссылок на другие НПА"
    parameters = {
        "type": "object",
        "properties": {
            "references": {
                "type": "array",
                "description": "Список ссылок для проверки"
            },
            "check_online": {
                "type": "boolean",
                "description": "Проверять ли ссылки онлайн на adilet.zan.kz"
            }
        },
        "required": ["references"]
    }

    def execute(
        self,
        references: List[str],
        check_online: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], ToolResult]:
        """
        Валидировать ссылки на НПА

        Args:
            references: Список ссылок
            check_online: Проверять онлайн
            **kwargs: Дополнительные параметры

        Returns:
            Результаты валидации
        """
        try:
            logger.info(f"Валидация {len(references)} ссылок на НПА")

            validation_results = []

            for ref in references:
                result = self._validate_reference(ref, check_online)
                validation_results.append(result)

            valid_count = sum(1 for r in validation_results if r["is_valid"])
            invalid_count = len(references) - valid_count

            return {
                "status": "success",
                "total_references": len(references),
                "valid_references": valid_count,
                "invalid_references": invalid_count,
                "results": validation_results
            }

        except Exception as e:
            error_msg = f"Ошибка при валидации ссылок: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }

    def _validate_reference(self, reference: str, check_online: bool) -> Dict[str, Any]:
        """Валидировать одну ссылку"""
        result = {
            "reference": reference,
            "is_valid": False,
            "issues": []
        }

        # Базовая проверка формата
        if not self._is_format_valid(reference):
            result["issues"].append("Неверный формат ссылки")
            return result

        # Онлайн проверка (если включена)
        if check_online:
            # TODO: Реализовать проверку через adilet.zan.kz
            pass

        result["is_valid"] = len(result["issues"]) == 0
        return result

    def _is_format_valid(self, reference: str) -> bool:
        """Проверить формат ссылки"""
        # Упрощенная проверка
        return len(reference) > 10
