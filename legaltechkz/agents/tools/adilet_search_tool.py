"""
Инструмент для поиска документов на adilet.zan.kz
"""

from typing import Dict, Any, List
import logging

from legaltechkz.agents.tools.base_tool import BaseTool
from legaltechkz.tools.adilet_search import AdiletSearchTool as AdiletSearch

logger = logging.getLogger("legaltechkz.agents.tools.adilet_search")


class AdiletSearchTool(BaseTool):
    """
    Инструмент для поиска НПА на adilet.zan.kz

    Используется агентом когда нужно:
    - Найти другие законы для проверки
    - Найти Конституцию РК
    - Найти подзаконные акты
    """

    def __init__(self):
        """Инициализация инструмента."""
        self.search_engine = AdiletSearch()
        super().__init__()

    def get_name(self) -> str:
        return "search_adilet"

    def get_description(self) -> str:
        return """Поиск нормативно-правовых актов на официальном сайте adilet.zan.kz

Используй этот инструмент когда нужно:
- Найти Конституцию РК для проверки соответствия
- Найти другой закон, упомянутый в статье
- Найти подзаконный акт для проверки противоречий
- Найти кодекс (Налоговый, Уголовный, Гражданский и т.д.)

Параметры:
- query (str): Поисковый запрос (например, "Конституция РК", "Налоговый кодекс")
- doc_type (str): Тип документа - "all", "code", "law", "decree", "order" (по умолчанию "all")
- year (str): Год принятия (опционально)

Возвращает: список найденных документов с названиями и URL"""

    def run(self, query: str, doc_type: str = "all", year: str = None) -> Dict[str, Any]:
        """
        Выполнить поиск на adilet.zan.kz

        Args:
            query: Поисковый запрос
            doc_type: Тип документа
            year: Год принятия

        Returns:
            Результаты поиска
        """
        logger.info(f"🔍 Поиск на adilet.zan.kz: '{query}'")

        try:
            results = self.search_engine.search(
                query=query,
                doc_type=doc_type,
                year=year,
                status="active"
            )

            # Форматируем результаты для агента
            if results and len(results) > 0:
                formatted_results = []
                for i, result in enumerate(results[:5], 1):  # Топ-5 результатов
                    formatted_results.append({
                        "rank": i,
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "doc_type": result.get("doc_type", ""),
                        "date": result.get("date", "")
                    })

                logger.info(f"✅ Найдено {len(formatted_results)} документов")

                return {
                    "success": True,
                    "query": query,
                    "total_found": len(results),
                    "results": formatted_results,
                    "message": f"Найдено {len(formatted_results)} документов по запросу '{query}'"
                }
            else:
                logger.warning(f"⚠️ Ничего не найдено по запросу '{query}'")
                return {
                    "success": False,
                    "query": query,
                    "results": [],
                    "message": f"По запросу '{query}' ничего не найдено"
                }

        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "message": f"Ошибка при поиске: {e}"
            }
