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
        checklist: str,
        batch_size: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Проанализировать несколько фрагментов группами для оптимизации.

        Args:
            fragments: Список фрагментов.
            checklist: Оглавление-чеклист.
            batch_size: Количество фрагментов для группового анализа (по умолчанию 5).

        Returns:
            Список результатов анализа.
        """
        total = len(fragments)
        logger.info(f"[{self.agent_name}] Начало batch-анализа: {total} фрагментов (группами по {batch_size})")

        results = []

        # Группируем фрагменты для эффективного анализа
        for i in range(0, total, batch_size):
            batch = fragments[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            logger.info(f"[{self.agent_name}] Обработка группы {batch_num}/{total_batches} ({len(batch)} статей)...")

            # Групповой анализ
            batch_results = self.analyze_fragment_group(batch, checklist)
            results.extend(batch_results)

            logger.info(f"[{self.agent_name}] Группа {batch_num}/{total_batches} завершена")

        logger.info(f"[{self.agent_name}] Batch-анализ завершён: {len(results)} результатов")

        return results

    def analyze_fragment_group(
        self,
        fragments: List[DocumentFragment],
        checklist: str
    ) -> List[Dict[str, Any]]:
        """
        Проанализировать группу фрагментов за один вызов LLM.

        Args:
            fragments: Группа фрагментов (обычно 5-10).
            checklist: Оглавление-чеклист.

        Returns:
            Список результатов для каждого фрагмента.
        """
        if len(fragments) == 1:
            # Для одного фрагмента используем обычный метод
            return [self.analyze_fragment(fragments[0], checklist)]

        # Формируем промпт для группового анализа
        system_prompt = self.get_system_prompt()

        # Собираем все фрагменты в один промпт
        fragments_text = "\n\n".join([
            f"### ФРАГМЕНТ {i+1}: {frag.number} ({frag.full_path})\n{frag.text}"
            for i, frag in enumerate(fragments)
        ])

        group_prompt = f"""**ГРУППОВОЙ АНАЛИЗ:** Проанализируй следующие фрагменты НПА последовательно.

**ОГЛАВЛЕНИЕ-ЧЕКЛИСТ:**
{checklist}

---

**ФРАГМЕНТЫ ДЛЯ АНАЛИЗА:**

{fragments_text}

---

**ИНСТРУКЦИЯ:**
Проанализируй КАЖДЫЙ фрагмент по отдельности согласно твоей методологии.
Для каждого фрагмента предоставь полный анализ с цитированием.

**ФОРМАТ ВЫВОДА:**
Для каждого фрагмента выведи результат в следующем формате:

```
=== АНАЛИЗ ФРАГМЕНТА: [номер] ===
[Полный детальный анализ согласно методологии]
=== КОНЕЦ АНАЛИЗА ФРАГМЕНТА: [номер] ===
```

Начинай анализ."""

        try:
            # Вызываем модель для группового анализа
            response = self.model.generate(
                prompt=group_prompt,
                system_message=system_prompt,
                temperature=0.1,
                max_tokens=8000  # Увеличенный лимит для группового анализа
            )

            # Парсим ответ и разделяем на отдельные результаты
            results = []
            for fragment in fragments:
                # Пытаемся извлечь анализ для каждого фрагмента
                # Упрощенный парсинг - ищем секцию для каждого номера
                fragment_analysis = self._extract_fragment_analysis(response, fragment.number)

                result = {
                    'agent': self.agent_name,
                    'fragment_type': fragment.type,
                    'fragment_number': fragment.number,
                    'fragment_path': fragment.full_path,
                    'analysis': fragment_analysis or response,  # Если не смогли распарсить - весь ответ
                    'success': True,
                    'group_analysis': True  # Маркер что это групповой анализ
                }

                self.analysis_results.append(result)
                results.append(result)

            logger.info(f"[{self.agent_name}] Групповой анализ завершён: {len(results)} фрагментов")

            return results

        except Exception as e:
            logger.error(f"[{self.agent_name}] Ошибка группового анализа: {e}")

            # Fallback - анализируем каждый фрагмент отдельно
            logger.warning(f"[{self.agent_name}] Переход на индивидуальный анализ")
            return [self.analyze_fragment(f, checklist) for f in fragments]

    def _extract_fragment_analysis(self, full_response: str, fragment_number: str) -> Optional[str]:
        """
        Извлечь анализ конкретного фрагмента из группового ответа.

        Args:
            full_response: Полный ответ LLM
            fragment_number: Номер фрагмента для извлечения

        Returns:
            Текст анализа для данного фрагмента или None
        """
        try:
            # Ищем маркеры начала и конца анализа фрагмента
            import re

            # Паттерн для поиска секции фрагмента
            pattern = rf"===\s*АНАЛИЗ ФРАГМЕНТА:\s*{re.escape(fragment_number)}\s*===(.*?)===\s*КОНЕЦ АНАЛИЗА ФРАГМЕНТА"

            match = re.search(pattern, full_response, re.DOTALL | re.IGNORECASE)

            if match:
                return match.group(1).strip()

            # Если не нашли с маркерами, возвращаем None
            return None

        except Exception as e:
            logger.debug(f"Не удалось извлечь анализ фрагмента {fragment_number}: {e}")
            return None

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
