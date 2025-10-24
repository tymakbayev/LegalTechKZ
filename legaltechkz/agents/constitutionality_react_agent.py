"""
ReAct Агент для проверки конституционности НПА

Это настоящий агент который:
1. Анализирует статью НПА
2. Извлекает ссылки на другие законы
3. Ищет Конституцию РК
4. Загружает нужные статьи Конституции
5. Сравнивает и выявляет противоречия
6. Формирует обоснованное заключение с цитатами
"""

from typing import Dict, Any
import logging

from legaltechkz.models.base.base_model import BaseModel
from legaltechkz.agents.react_agent import ReActAgent
from legaltechkz.agents.tools import (
    AdiletSearchTool,
    DocumentFetchTool,
    ReferenceExtractorTool
)
from legaltechkz.expertise.document_parser import DocumentFragment

logger = logging.getLogger("legaltechkz.agents.constitutionality")


class ConstitutionalityReActAgent:
    """
    ReAct агент для проверки конституционности.

    Автономно:
    - Анализирует статью
    - Извлекает упоминания законов
    - Ищет и загружает Конституцию РК
    - Сравнивает положения
    - Выявляет противоречия
    """

    def __init__(self, model: BaseModel):
        """
        Инициализация агента.

        Args:
            model: LLM модель для рассуждений
        """
        self.model = model

        # Создаем инструменты
        tools = [
            AdiletSearchTool(),
            DocumentFetchTool(),
            ReferenceExtractorTool()
        ]

        # Создаем ReAct агента
        self.agent = ReActAgent(
            model=model,
            tools=tools,
            agent_name="Фильтр Конституционности (ReAct)",
            max_iterations=10,
            verbose=True
        )

        logger.info("Инициализирован ConstitutionalityReActAgent")

    def analyze_article(self, article: DocumentFragment) -> Dict[str, Any]:
        """
        Проанализировать статью на соответствие Конституции.

        Args:
            article: Фрагмент документа (статья)

        Returns:
            Результат анализа
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Анализ статьи: {article.full_path}")
        logger.info(f"{'='*80}\n")

        # Формируем задачу для агента
        task = self._build_task(article)

        # Контекст
        context = {
            "article_number": article.number,
            "article_path": article.full_path,
            "article_text": article.text
        }

        # Запускаем ReAct агента
        result = self.agent.run(task=task, context=context)

        # Формируем результат для системы
        if result["success"]:
            return {
                "success": True,
                "agent": "Фильтр Конституционности (ReAct)",
                "fragment_type": article.type,
                "fragment_number": article.number,
                "fragment_path": article.full_path,
                "analysis": result["answer"],
                "iterations": result["iterations"],
                "thinking_process": self._format_thinking_process(result["history"])
            }
        else:
            return {
                "success": False,
                "agent": "Фильтр Конституционности (ReAct)",
                "fragment_number": article.number,
                "error": result.get("answer", "Неизвестная ошибка")
            }

    def _build_task(self, article: DocumentFragment) -> str:
        """Формирование задачи для агента."""
        return f"""Проведи проверку соответствия статьи НПА Конституции РК.

СТАТЬЯ ДЛЯ АНАЛИЗА:
Номер: {article.number}
Путь: {article.full_path}
Текст:
{article.text}

ТВОЯ ЗАДАЧА:

1. **Извлеки ссылки**: Найди все упоминания других законов, кодексов, Конституции в тексте статьи
   - Используй инструмент extract_references

2. **Найди Конституцию РК**: Если в статье упоминается Конституция или затрагиваются конституционные права
   - Используй инструмент search_adilet с запросом "Конституция Республики Казахстан"

3. **Загрузи Конституцию**: Загрузи текст Конституции РК
   - Используй инструмент fetch_document с URL найденной Конституции

4. **Проанализируй соответствие**: Сравни статью НПА с релевантными статьями Конституции:
   - Проверь на ограничение конституционных прав (ст. 39 Конституции)
   - Проверь компетенцию (ст. 61 Конституции - исключительная компетенция Парламента)
   - Проверь на противоречия с конституционными принципами

5. **Если найдены противоречия**: Загрузи конкретные статьи Конституции для цитирования
   - Используй fetch_document с параметром article_number

6. **Сформируй заключение**: Дай детальный анализ с:
   - Выводом (СООТВЕТСТВУЕТ / НЕ СООТВЕТСТВУЕТ / ТРЕБУЕТ УТОЧНЕНИЯ)
   - Обоснованием с цитатами из Конституции
   - Рекомендациями по доработке (если нужно)

ВАЖНО:
- Используй РЕАЛЬНЫЕ инструменты для поиска и загрузки документов
- Цитируй КОНКРЕТНЫЕ статьи Конституции с их текстом
- Будь объективным и обоснованным
- Если не уверен - используй инструменты для проверки

Начинай анализ!"""

    def _format_thinking_process(self, history: list) -> str:
        """
        Форматирование процесса мышления агента для отображения.

        Args:
            history: История ReAct итераций

        Returns:
            Форматированный процесс мышления
        """
        formatted = []
        for entry in history:
            iteration = entry["iteration"]
            thought = entry["thought"][:300]  # Первые 300 символов
            action = entry["action"]
            observation = entry["observation"]

            formatted.append(f"Итерация {iteration}:")
            formatted.append(f"🧠 Thought: {thought}...")
            formatted.append(f"⚡ Action: {action.get('tool')} {action.get('params')}")
            formatted.append(f"👁️ Result: {observation.get('message', str(observation)[:200])}")
            formatted.append("")

        return "\n".join(formatted)

    def analyze_batch(
        self,
        articles: list,
        checklist: str,
        batch_size: int = 5,
        max_workers: int = 3
    ) -> list:
        """
        Анализ группы статей (для совместимости с существующей системой).

        Args:
            articles: Список статей
            checklist: Чеклист (не используется в ReAct)
            batch_size: Размер группы (не используется в ReAct)
            max_workers: Количество потоков (не используется в ReAct)

        Returns:
            Результаты анализа
        """
        results = []

        logger.info(f"Начало ReAct анализа {len(articles)} статей")

        for i, article in enumerate(articles, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Статья {i}/{len(articles)}: {article.full_path}")
            logger.info(f"{'='*80}\n")

            result = self.analyze_article(article)
            results.append(result)

        logger.info(f"\nЗавершен ReAct анализ: {len(results)} результатов")

        return results
