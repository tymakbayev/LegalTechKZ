"""
Базовый класс для инструментов (tools) агентов.

Инструменты - это действия, которые агент может выполнять:
- Поиск документов
- Загрузка и парсинг НПА
- Извлечение ссылок
- Сравнение статей
- Проверка с Конституцией
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("legaltechkz.agents.tools")


class BaseTool(ABC):
    """
    Базовый класс для инструмента агента.

    Каждый инструмент имеет:
    - Название (name)
    - Описание (description) - для LLM чтобы знать когда использовать
    - Метод run() - выполнение действия
    """

    def __init__(self):
        """Инициализация инструмента."""
        self.name = self.get_name()
        self.description = self.get_description()
        logger.info(f"Инициализирован инструмент: {self.name}")

    @abstractmethod
    def get_name(self) -> str:
        """
        Получить название инструмента.

        Returns:
            Название инструмента (например, "search_adilet")
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Получить описание инструмента для LLM.

        Описание должно четко объяснять:
        - Что делает инструмент
        - Когда его использовать
        - Какие параметры принимает

        Returns:
            Описание инструмента
        """
        pass

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Выполнить действие инструмента.

        Args:
            **kwargs: Параметры для выполнения

        Returns:
            Результат выполнения в виде словаря
        """
        pass

    def get_tool_signature(self) -> Dict[str, Any]:
        """
        Получить сигнатуру инструмента для промпта LLM.

        Returns:
            Словарь с названием и описанием
        """
        return {
            "name": self.name,
            "description": self.description
        }

    def log_usage(self, params: Dict[str, Any], result: Dict[str, Any]):
        """
        Логирование использования инструмента.

        Args:
            params: Параметры вызова
            result: Результат выполнения
        """
        logger.info(f"[{self.name}] Вызван с параметрами: {params}")
        logger.debug(f"[{self.name}] Результат: {result}")
