"""
Базовый класс для всех экспертных агентов.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

from legaltechkz.expertise.document_parser import DocumentFragment
from legaltechkz.models.base.base_model import BaseModel

logger = logging.getLogger("legaltechkz.expertise.base_expert")


class BaseExpertAgent(ABC):
    """
    Базовый класс для экспертного агента.

    Каждый агент проводит свой тип экспертизы с использованием LLM.
    """

    def __init__(self, model: BaseModel, agent_name: str):
        """
        Инициализация агента.

        Args:
            model: Модель LLM для анализа.
            agent_name: Название агента.
        """
        self.model = model
        self.agent_name = agent_name
        self.analysis_results: List[Dict[str, Any]] = []

        logger.info(f"Инициализирован агент: {agent_name} (модель: {model.model_name})")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Получить системный промпт для агента.

        Returns:
            Текст системного промпта.
        """
        pass

    @abstractmethod
    def get_analysis_prompt(self, fragment: DocumentFragment, checklist: str) -> str:
        """
        Получить промпт для анализа конкретного фрагмента.

        Args:
            fragment: Фрагмент документа для анализа.
            checklist: Оглавление-чеклист для контроля.

        Returns:
            Текст промпта для анализа.
        """
        pass

    def analyze_fragment(
        self,
        fragment: DocumentFragment,
        checklist: str
    ) -> Dict[str, Any]:
        """
        Проанализировать один фрагмент документа.

        Args:
            fragment: Фрагмент для анализа.
            checklist: Оглавление-чеклист.

        Returns:
            Результат анализа.
        """
        logger.info(f"[{self.agent_name}] Анализ: {fragment.full_path}")

        # Формируем промпт
        system_prompt = self.get_system_prompt()
        analysis_prompt = self.get_analysis_prompt(fragment, checklist)

        # Вызываем модель
        try:
            response = self.model.generate(
                prompt=analysis_prompt,
                system_message=system_prompt,
                temperature=0.1,
                max_tokens=4000
            )

            result = {
                'agent': self.agent_name,
                'fragment_type': fragment.type,
                'fragment_number': fragment.number,
                'fragment_path': fragment.full_path,
                'analysis': response,
                'success': True
            }

            self.analysis_results.append(result)

            logger.info(f"[{self.agent_name}] Анализ {fragment.number} завершён")

            return result

        except Exception as e:
            logger.error(f"[{self.agent_name}] Ошибка при анализе {fragment.number}: {e}")

            error_result = {
                'agent': self.agent_name,
                'fragment_type': fragment.type,
                'fragment_number': fragment.number,
                'fragment_path': fragment.full_path,
                'analysis': None,
                'error': str(e),
                'success': False
            }

            self.analysis_results.append(error_result)

            return error_result

    def analyze_batch(
        self,
        fragments: List[DocumentFragment],
        checklist: str
    ) -> List[Dict[str, Any]]:
        """
        Проанализировать несколько фрагментов.

        Args:
            fragments: Список фрагментов.
            checklist: Оглавление-чеклист.

        Returns:
            Список результатов анализа.
        """
        logger.info(f"[{self.agent_name}] Начало batch-анализа: {len(fragments)} фрагментов")

        results = []

        for fragment in fragments:
            result = self.analyze_fragment(fragment, checklist)
            results.append(result)

        logger.info(f"[{self.agent_name}] Batch-анализ завершён")

        return results

    def get_results_summary(self) -> Dict[str, Any]:
        """
        Получить сводку по результатам анализа.

        Returns:
            Словарь со сводкой.
        """
        total = len(self.analysis_results)
        successful = sum(1 for r in self.analysis_results if r.get('success', False))
        failed = total - successful

        return {
            'agent': self.agent_name,
            'total_analyzed': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0.0
        }
