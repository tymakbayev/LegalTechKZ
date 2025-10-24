"""
Инструмент для извлечения ссылок на другие НПА из текста
"""

from typing import Dict, Any, List
import logging
import re

from legaltechkz.agents.tools.base_tool import BaseTool

logger = logging.getLogger("legaltechkz.agents.tools.reference_extractor")


class ReferenceExtractorTool(BaseTool):
    """
    Инструмент для извлечения ссылок на другие НПА.

    Используется когда агент хочет:
    - Найти все упоминания других законов в тексте
    - Извлечь ссылки на Конституцию
    - Найти упоминания кодексов и подзаконных актов
    """

    def __init__(self):
        """Инициализация инструмента."""
        super().__init__()

        # Паттерны для поиска ссылок
        self.patterns = {
            "constitution": r"Конституци[июяей]\s+(?:Республики\s+)?Казахстана?",
            "code": r"([А-Яа-я]+)\s+кодекс[аеу]?",
            "law": r"Закон[аеу]?\s+(?:Республики\s+Казахстан\s+)?[«\"]([^»\"]+)[»\"]",
            "law_date": r"Закон[аеу]?\s+РК\s+от\s+(\d{1,2}\s+\w+\s+\d{4}\s+года)",
            "article_ref": r"стать[иея]\s+(\d+)",
            "paragraph_ref": r"пункт[ауе]?\s+(\d+)"
        }

    def get_name(self) -> str:
        return "extract_references"

    def get_description(self) -> str:
        return """Извлечение ссылок на другие НПА из текста

Используй этот инструмент когда нужно:
- Найти все упоминания других законов в статье
- Извлечь ссылки на Конституцию РК
- Найти упоминания кодексов (Налоговый, Уголовный и т.д.)
- Извлечь ссылки на статьи других законов

Параметры:
- text (str): Текст для анализа

Возвращает: список найденных ссылок с типами (Конституция, Закон, Кодекс, статья)"""

    def run(self, text: str) -> Dict[str, Any]:
        """
        Извлечь ссылки из текста.

        Args:
            text: Текст для анализа

        Returns:
            Найденные ссылки
        """
        logger.info(f"📎 Извлечение ссылок из текста ({len(text)} символов)")

        try:
            references = {
                "constitution": [],
                "codes": [],
                "laws": [],
                "articles": [],
                "paragraphs": []
            }

            # Поиск ссылок на Конституцию
            constitution_matches = re.finditer(self.patterns["constitution"], text, re.IGNORECASE)
            for match in constitution_matches:
                references["constitution"].append({
                    "text": match.group(0),
                    "position": match.start()
                })

            # Поиск кодексов
            code_matches = re.finditer(self.patterns["code"], text, re.IGNORECASE)
            for match in code_matches:
                code_name = match.group(1)
                references["codes"].append({
                    "name": f"{code_name} кодекс",
                    "text": match.group(0),
                    "position": match.start()
                })

            # Поиск законов (по названию)
            law_matches = re.finditer(self.patterns["law"], text, re.IGNORECASE)
            for match in law_matches:
                law_name = match.group(1)
                references["laws"].append({
                    "name": law_name,
                    "text": match.group(0),
                    "position": match.start()
                })

            # Поиск законов (по дате)
            law_date_matches = re.finditer(self.patterns["law_date"], text, re.IGNORECASE)
            for match in law_date_matches:
                date = match.group(1)
                references["laws"].append({
                    "date": date,
                    "text": match.group(0),
                    "position": match.start()
                })

            # Поиск ссылок на статьи
            article_matches = re.finditer(self.patterns["article_ref"], text, re.IGNORECASE)
            for match in article_matches:
                article_num = match.group(1)
                references["articles"].append({
                    "number": int(article_num),
                    "text": match.group(0),
                    "position": match.start()
                })

            # Поиск ссылок на пункты
            paragraph_matches = re.finditer(self.patterns["paragraph_ref"], text, re.IGNORECASE)
            for match in paragraph_matches:
                paragraph_num = match.group(1)
                references["paragraphs"].append({
                    "number": int(paragraph_num),
                    "text": match.group(0),
                    "position": match.start()
                })

            # Удаляем дубликаты
            for key in references:
                unique_refs = []
                seen = set()
                for ref in references[key]:
                    ref_str = str(ref.get("text", ""))
                    if ref_str not in seen:
                        seen.add(ref_str)
                        unique_refs.append(ref)
                references[key] = unique_refs

            total_refs = sum(len(v) for v in references.values())

            logger.info(f"✅ Найдено {total_refs} ссылок")
            logger.debug(f"   - Конституция: {len(references['constitution'])}")
            logger.debug(f"   - Кодексы: {len(references['codes'])}")
            logger.debug(f"   - Законы: {len(references['laws'])}")
            logger.debug(f"   - Статьи: {len(references['articles'])}")

            return {
                "success": True,
                "total_references": total_refs,
                "references": references,
                "message": f"Найдено {total_refs} ссылок на другие НПА"
            }

        except Exception as e:
            logger.error(f"❌ Ошибка извлечения ссылок: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Ошибка при извлечении ссылок: {e}"
            }
