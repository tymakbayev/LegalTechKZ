"""
ReAct Agent - Агент с циклом Reasoning and Acting

Архитектура:
1. Thought (Мышление): Агент анализирует ситуацию и решает что делать
2. Action (Действие): Агент выбирает инструмент и выполняет действие
3. Observation (Наблюдение): Агент получает результат действия
4. Reflection (Рефлексия): Агент обновляет свое понимание и решает продолжать или завершить

Цикл повторяется до получения финального ответа.
"""

from typing import Dict, Any, List, Optional
import logging
import json
import re

from legaltechkz.models.base.base_model import BaseModel
from legaltechkz.agents.tools.base_tool import BaseTool

logger = logging.getLogger("legaltechkz.agents.react")


class ReActAgent:
    """
    Агент с циклом Reasoning and Acting.

    Использует паттерн ReAct для автономного решения задач:
    - Анализирует ситуацию
    - Выбирает инструменты
    - Выполняет действия
    - Обновляет понимание
    - Принимает решения
    """

    def __init__(
        self,
        model: BaseModel,
        tools: List[BaseTool],
        agent_name: str,
        max_iterations: int = 10,
        verbose: bool = True
    ):
        """
        Инициализация ReAct агента.

        Args:
            model: LLM модель для рассуждений
            tools: Список доступных инструментов
            agent_name: Название агента
            max_iterations: Максимум итераций ReAct цикла
            verbose: Подробное логирование
        """
        self.model = model
        self.tools = {tool.name: tool for tool in tools}
        self.agent_name = agent_name
        self.max_iterations = max_iterations
        self.verbose = verbose

        self.memory: List[Dict[str, Any]] = []
        self.current_task = None

        logger.info(f"Инициализирован ReAct агент: {agent_name}")
        logger.info(f"Доступных инструментов: {len(self.tools)}")
        for tool_name in self.tools.keys():
            logger.info(f"  - {tool_name}")

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Выполнить задачу с использованием ReAct цикла.

        Args:
            task: Описание задачи
            context: Дополнительный контекст

        Returns:
            Результат выполнения задачи
        """
        self.current_task = task
        self.memory = []
        context = context or {}

        logger.info(f"\n{'='*80}")
        logger.info(f"[{self.agent_name}] Новая задача: {task[:100]}...")
        logger.info(f"{'='*80}\n")

        # ReAct цикл
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"\n--- Итерация {iteration}/{self.max_iterations} ---\n")

            # 1. THOUGHT: Что агент думает делать
            thought = self._generate_thought(task, context)
            self._log_thought(thought, iteration)

            # Проверка на завершение
            if self._is_final_answer(thought):
                final_answer = self._extract_final_answer(thought)
                logger.info(f"\n🎯 Финальный ответ получен на итерации {iteration}")
                return self._build_result(final_answer, success=True)

            # 2. ACTION: Какое действие выполнить
            action = self._parse_action(thought)
            if not action:
                logger.warning("⚠️ Не удалось распарсить действие, продолжаем...")
                continue

            self._log_action(action, iteration)

            # 3. OBSERVATION: Выполнение действия и получение результата
            observation = self._execute_action(action)
            self._log_observation(observation, iteration)

            # 4. REFLECTION: Обновление памяти
            self.memory.append({
                "iteration": iteration,
                "thought": thought,
                "action": action,
                "observation": observation
            })

        # Если достигли лимита итераций
        logger.warning(f"⚠️ Достигнут лимит итераций ({self.max_iterations})")
        return self._build_result(
            "Не удалось завершить задачу в рамках максимального числа итераций",
            success=False
        )

    def _generate_thought(self, task: str, context: Dict[str, Any]) -> str:
        """
        Генерация мысли агента (Thought).

        Агент анализирует:
        - Текущую задачу
        - Историю действий
        - Доступные инструменты
        - Что делать дальше
        """
        # Формируем промпт для рассуждения
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_thought_prompt(task, context)

        # Запрашиваем у модели рассуждение
        thought = self.model.generate(
            prompt=user_prompt,
            system_message=system_prompt,
            temperature=0.1,
            max_tokens=1000
        )

        return thought.strip()

    def _build_system_prompt(self) -> str:
        """Системный промпт для агента."""
        tools_description = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools.values()
        ])

        return f"""Ты - {self.agent_name}, эксперт по правовому анализу НПА Казахстана.

Ты используешь цикл ReAct (Reasoning and Acting) для решения задач:

1. THOUGHT (Мышление): Анализируй ситуацию и решай что делать дальше
2. ACTION (Действие): Выбери инструмент и выполни действие
3. OBSERVATION (Наблюдение): Получи результат
4. REFLECTION (Рефлексия): Обнови понимание

ДОСТУПНЫЕ ИНСТРУМЕНТЫ:
{tools_description}

ФОРМАТ ОТВЕТА:

Thought: [Твои рассуждения о том, что делать дальше]
Action: [Название инструмента]
Action Input: [Параметры для инструмента в JSON]

ИЛИ если задача решена:

Thought: Я собрал всю необходимую информацию и готов дать финальный ответ
Final Answer: [Детальный ответ на задачу]

ВАЖНО:
- Всегда начинай с "Thought:"
- Используй инструменты для получения информации
- Проверяй ссылки на другие законы
- Загружай упомянутые документы
- Сравнивай статьи разных НПА
- Давай обоснованные выводы с цитатами"""

    def _build_thought_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Промпт для генерации мысли."""
        # История предыдущих действий
        history = ""
        if self.memory:
            history = "\n\nИСТОРИЯ ДЕЙСТВИЙ:\n"
            for entry in self.memory[-5:]:  # Последние 5 действий
                history += f"\nИтерация {entry['iteration']}:\n"
                history += f"Thought: {entry['thought'][:200]}...\n"
                history += f"Action: {entry['action'].get('tool', 'unknown')}\n"
                history += f"Observation: {str(entry['observation'])[:200]}...\n"

        # Контекст задачи
        context_str = ""
        if context:
            context_str = f"\n\nКОНТЕКСТ:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n"

        return f"""ЗАДАЧА: {task}
{context_str}
{history}

Что делать дальше? (Используй формат Thought → Action или Final Answer)"""

    def _is_final_answer(self, thought: str) -> bool:
        """Проверка - является ли ответ финальным."""
        return "Final Answer:" in thought or "Финальный ответ:" in thought

    def _extract_final_answer(self, thought: str) -> str:
        """Извлечение финального ответа."""
        if "Final Answer:" in thought:
            return thought.split("Final Answer:")[1].strip()
        elif "Финальный ответ:" in thought:
            return thought.split("Финальный ответ:")[1].strip()
        return thought

    def _parse_action(self, thought: str) -> Optional[Dict[str, Any]]:
        """
        Парсинг действия из мысли агента.

        Ожидаемый формат:
        Action: tool_name
        Action Input: {"param": "value"}
        """
        try:
            # Ищем Action
            action_match = re.search(r'Action:\s*([^\n]+)', thought)
            if not action_match:
                return None

            tool_name = action_match.group(1).strip()

            # Ищем Action Input
            input_match = re.search(r'Action Input:\s*(\{[^}]+\})', thought, re.DOTALL)
            if input_match:
                try:
                    tool_params = json.loads(input_match.group(1))
                except json.JSONDecodeError:
                    # Пробуем без JSON
                    tool_params = {"input": input_match.group(1)}
            else:
                tool_params = {}

            return {
                "tool": tool_name,
                "params": tool_params
            }

        except Exception as e:
            logger.error(f"Ошибка парсинга действия: {e}")
            return None

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение действия."""
        tool_name = action.get("tool", "").strip()
        params = action.get("params", {})

        # Проверяем наличие инструмента
        if tool_name not in self.tools:
            logger.warning(f"⚠️ Инструмент '{tool_name}' не найден")
            return {
                "success": False,
                "error": f"Инструмент '{tool_name}' не существует",
                "available_tools": list(self.tools.keys())
            }

        # Выполняем инструмент
        try:
            tool = self.tools[tool_name]
            result = tool.run(**params)
            return result

        except Exception as e:
            logger.error(f"❌ Ошибка выполнения {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _build_result(self, answer: str, success: bool) -> Dict[str, Any]:
        """Формирование финального результата."""
        return {
            "success": success,
            "answer": answer,
            "agent": self.agent_name,
            "iterations": len(self.memory),
            "history": self.memory
        }

    def _log_thought(self, thought: str, iteration: int):
        """Логирование мысли."""
        if self.verbose:
            logger.info(f"🧠 Thought (итерация {iteration}):")
            logger.info(f"   {thought[:500]}{'...' if len(thought) > 500 else ''}\n")

    def _log_action(self, action: Dict[str, Any], iteration: int):
        """Логирование действия."""
        if self.verbose:
            logger.info(f"⚡ Action (итерация {iteration}):")
            logger.info(f"   Инструмент: {action.get('tool')}")
            logger.info(f"   Параметры: {json.dumps(action.get('params', {}), ensure_ascii=False)}\n")

    def _log_observation(self, observation: Dict[str, Any], iteration: int):
        """Логирование наблюдения."""
        if self.verbose:
            logger.info(f"👁️ Observation (итерация {iteration}):")
            obs_str = json.dumps(observation, ensure_ascii=False, indent=2)
            logger.info(f"   {obs_str[:500]}{'...' if len(obs_str) > 500 else ''}\n")
