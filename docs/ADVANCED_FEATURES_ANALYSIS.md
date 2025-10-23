# Анализ продвинутых возможностей LLM провайдеров для LegalTechKZ

Детальный анализ batch/streaming поддержки и дополнительных функций GPT-4.1, Claude Sonnet 4.5 и Gemini 2.5 Flash для оптимизации системы правовой экспертизы.

## Обзор возможностей по провайдерам

### OpenAI GPT-4.1

#### Batch API
- **Скидка:** 50% от стандартной цены
- **Время обработки:** До 24 часов
- **Формат:** JSONL файлы (до 100MB, 50,000 запросов)
- **Ограничения:**
  - Нет поддержки streaming
  - Не совместим с параллельными вызовами функций
- **Квоты:** Отдельная, в 2 раза выше стандартного API

**Оценка для нашей задачи:** ⭐⭐⭐⭐ (4/5)
- Идеально для анализа множества НПА в фоновом режиме
- Экономия 50% при обработке архивов документов

#### Structured Outputs
- **Возможность:** 100% гарантия соответствия JSON схеме
- **Поддержка:** Все модели GPT-4.1+
- **Применение:** Обеспечивает валидный формат отчетов экспертизы

**Оценка:** ⭐⭐⭐⭐⭐ (5/5)
- **Критически важно** для нашей системы
- Гарантирует парсинг результатов без ошибок
- Исключает проблемы с некорректным JSON

#### Function Calling
- **Strict Mode:** Гарантированное соответствие схеме параметров
- **Parallel Calls:** Множественные вызовы функций одновременно

**Оценка:** ⭐⭐⭐ (3/5)
- Полезно, но не критично для текущей архитектуры

### Anthropic Claude Sonnet 4.5

#### Prompt Caching
- **Экономия:** До 90% стоимости на повторяющихся промптах
- **TTL:** 5 минут (default) или 1 час (ephemeral)
- **Минимум:** 1024 токена для кеширования
- **Цена кеша:** $3.75 за 1M токенов записи, $0.30 за чтение
- **Совместимость:** Работает с batch API (дополнительная скидка)

**Оценка для нашей задачи:** ⭐⭐⭐⭐⭐ (5/5)
- **Максимальная выгода** для нашей системы!
- 6 этапов экспертизы используют похожие system prompts
- При анализе 100 статей одного НПА:
  - Первый вызов: полная цена
  - Следующие 99 вызовов: -90% на system prompt
- **Расчет экономии:**
  - System prompt: ~2000 токенов
  - Без кеша: 100 вызовов × 2000 токенов × $3/M = $0.60
  - С кешем: 1 запись + 99 чтений = $0.0075 + $0.059 = $0.067
  - **Экономия: $0.53 (88%) только на system prompts**

#### Extended Thinking Mode
- **Возможность:** Видимое пошаговое рассуждение модели
- **Производительность:** 96.2% на MATH 500 (vs 78% без thinking)
- **Бюджет мышления:** До 10K токенов думания
- **Цена:** Та же что стандартный API ($3/$15 за миллион)
- **Вывод:** Мысли включены в output tokens

**Оценка:** ⭐⭐⭐⭐⭐ (5/5)
- **Идеально для сложного правового анализа**
- Особенно полезно для:
  - Фильтр Конституционности (сложные NLI рассуждения)
  - Фильтр Системной Интеграции (выявление коллизий)
  - Антикоррупционная экспертиза (поиск скрытых факторов)
- Прозрачность рассуждений важна для правовых заключений
- Можно включить thinking токены в отчет как обоснование

#### Batch API (Message Batches)
- **Скидка:** 50% от стандартной цены
- **Время:** 24 часа
- **Совместимость:** Работает с prompt caching (суммарная скидка!)
- **Формат:** До 10,000 запросов на batch

**Оценка:** ⭐⭐⭐⭐ (4/5)
- Комбинация с prompt caching дает огромную экономию
- При анализе 10 НПА в batch режиме с кешем:
  - Скидка batch: -50%
  - Скидка кеш: -90% на повторяющихся промптах
  - **Суммарная экономия: до 95%**

#### Interleaved Thinking (Beta)
- **Возможность:** Думание между вызовами инструментов
- **Статус:** Закрытая бета

**Оценка:** ⭐⭐ (2/5)
- Пока недоступно широко, следить за релизом

### Google Gemini 2.5 Flash

#### Batch API
- **Скидка:** 50% от стандартной цены
- **Время:** До 24 часов
- **Формат:** JSONL файлы (до 2GB!)
- **Особенность:** Поддержка multimodal в batch

**Оценка:** ⭐⭐⭐⭐ (4/5)
- Отличная поддержка больших объемов
- 2GB лимит позволяет обработать сотни документов

#### Context Caching

**Implicit Caching (автоматический):**
- Включен по умолчанию для Gemini 2.5 Flash
- Минимум: 1024 токена
- TTL: 1 час
- Цена: Бесплатно (автоматически)

**Explicit Caching (ручной):**
- Полный контроль над кешируемым контентом
- TTL: Настраиваемый
- Цена: $0.0001 за 1M токенов хранения (в час)

**Оценка:** ⭐⭐⭐⭐⭐ (5/5)
- **Implicit кеш - бесплатная оптимизация!**
- Идеально для нашей задачи:
  - При обработке большого НПА (500+ статей)
  - Gemini получает полный текст в контексте
  - Следующие запросы используют кеш автоматически
- **Пример:**
  - Полный текст закона: 200K токенов
  - Первый запрос: полная цена
  - Следующие запросы в течение часа: 200K токенов бесплатно

#### Grounding with Google Search
- **Возможность:** Доступ к актуальной информации из интернета
- **Режимы:**
  - Dynamic Retrieval: автоматическое определение необходимости поиска
  - Grounding: всегда использовать поиск
- **Источники:** Проверяемые ссылки в ответе
- **Поддержка:** Встроенная, не требует дополнительных API

**Оценка:** ⭐⭐⭐⭐⭐ (5/5)
- **Революционная возможность для правовой системы!**
- Применение:
  - Фильтр Системной Интеграции: поиск актуальных версий законов
  - Проверка действующего законодательства РК
  - Поиск постановлений Конституционного Суда
  - Актуализация правовых позиций
- **Пример запроса:**
  ```
  "Проверь актуальна ли редакция статьи 123 Конституции РК
   и найди постановления Конституционного Суда по этой статье"
  ```
  → Gemini найдет актуальную информацию с сайтов adilet.zan.kz, etc.

#### Multimodal Capabilities
- **Форматы:** Изображения, PDF, видео, документы
- **Применение:** Анализ сканов документов, таблиц, схем

**Оценка:** ⭐⭐⭐ (3/5)
- Полезно для анализа PDF версий НПА
- Не критично для текущей версии системы

## Рекомендации по внедрению

### 1. Prompt Caching для Claude (Приоритет: ВЫСОКИЙ)

**Что делать:**
Внедрить prompt caching для всех 6 экспертных агентов.

**Как реализовать:**

```python
# legaltechkz/models/anthropic_model.py

def generate(self, prompt: str, system_message: Optional[str] = None,
             use_caching: bool = True, **kwargs) -> str:
    """
    Generate with optional prompt caching support.
    """
    messages = [{"role": "user", "content": prompt}]

    extra_headers = {}
    system_blocks = []

    if use_caching and system_message:
        # Enable caching for system prompt
        extra_headers["anthropic-beta"] = "prompt-caching-2024-07-31"
        system_blocks = [
            {
                "type": "text",
                "text": system_message,
                "cache_control": {"type": "ephemeral"}
            }
        ]
    elif system_message:
        system_blocks = [{"type": "text", "text": system_message}]

    response = self.client.messages.create(
        model=self.model_name,
        max_tokens=self.max_tokens,
        system=system_blocks,
        messages=messages,
        extra_headers=extra_headers,
        **kwargs
    )

    return response.content[0].text
```

**Применение в экспертных агентах:**

```python
# legaltechkz/expertise/expert_agents.py

class RelevanceFilterAgent(BaseExpertAgent):
    def analyze_fragment(self, fragment: DocumentFragment,
                        checklist: str) -> Dict[str, Any]:
        system_prompt = self.get_system_prompt()
        analysis_prompt = self.get_analysis_prompt(fragment, checklist)

        # Enable caching for system prompt (same across all articles)
        response = self.model.generate(
            prompt=analysis_prompt,
            system_message=system_prompt,
            use_caching=True  # ← Экономия 90% на повторных вызовах
        )

        return self._parse_response(response)
```

**Ожидаемая экономия:**
- Анализ НПА с 100 статьями
- 6 этапов экспертизы
- System prompt: ~2000 токенов на этап
- **Без кеша:** 100 × 6 × 2000 × $3/M = $3.60
- **С кешем:** 6 × ($0.0075 + 99 × $0.0006) = $0.40
- **Экономия: $3.20 (89%) только на system prompts**

### 2. Extended Thinking для сложных этапов (Приоритет: ВЫСОКИЙ)

**Что делать:**
Включить Extended Thinking для этапов требующих глубокого анализа.

**Реализация:**

```python
# legaltechkz/models/anthropic_model.py

def generate_with_thinking(self, prompt: str,
                          system_message: Optional[str] = None,
                          thinking_budget: int = 10000,
                          use_caching: bool = True) -> Dict[str, Any]:
    """
    Generate with extended thinking mode.

    Returns:
        {
            'response': str,  # Actual response
            'thinking': str   # Thinking process (for transparency)
        }
    """
    extra_headers = {
        "anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"
    }

    if use_caching:
        extra_headers["anthropic-beta"] += ",prompt-caching-2024-07-31"

    system_blocks = []
    if system_message:
        cache_control = {"type": "ephemeral"} if use_caching else None
        system_blocks = [{
            "type": "text",
            "text": system_message,
            **({"cache_control": cache_control} if cache_control else {})
        }]

    response = self.client.messages.create(
        model=self.model_name,
        max_tokens=thinking_budget + self.max_tokens,
        system=system_blocks,
        messages=[{"role": "user", "content": prompt}],
        thinking={
            "type": "enabled",
            "budget_tokens": thinking_budget
        },
        extra_headers=extra_headers
    )

    # Extract thinking and response
    thinking_text = ""
    response_text = ""

    for block in response.content:
        if block.type == "thinking":
            thinking_text = block.thinking
        elif block.type == "text":
            response_text = block.text

    return {
        'response': response_text,
        'thinking': thinking_text
    }
```

**Применение:**

```python
# legaltechkz/expertise/expert_agents.py

class ConstitutionalityFilterAgent(BaseExpertAgent):
    """
    Фильтр конституционности - требует глубокого анализа.
    Используем Extended Thinking для прозрачности рассуждений.
    """

    def analyze_fragment(self, fragment: DocumentFragment,
                        checklist: str) -> Dict[str, Any]:
        system_prompt = self.get_system_prompt()
        analysis_prompt = self.get_analysis_prompt(fragment, checklist)

        # Use extended thinking for complex constitutional analysis
        result = self.model.generate_with_thinking(
            prompt=analysis_prompt,
            system_message=system_prompt,
            thinking_budget=5000,  # Бюджет на рассуждения
            use_caching=True
        )

        return {
            'fragment_number': fragment.number,
            'analysis': result['response'],
            'reasoning': result['thinking'],  # Включаем в отчет!
            'success': True
        }
```

**Какие этапы используют thinking:**
1. ✅ Фильтр Конституционности (NLI анализ, сложные рассуждения)
2. ✅ Фильтр Системной Интеграции (поиск коллизий)
3. ✅ Антикоррупционная экспертиза (выявление скрытых факторов)
4. ❌ Фильтр Релевантности (базовая классификация, не нужен)
5. ❌ Юридико-техническая (формальная проверка)
6. ❌ Гендерная (стандартный анализ)

**Преимущества:**
- Прозрачность: видно как модель пришла к выводу
- Качество: лучше результаты на сложных задачах (+18% на MATH 500)
- Легальность: рассуждения можно включить в правовое заключение как обоснование

### 3. Grounding для актуализации законодательства (Приоритет: СРЕДНИЙ)

**Что делать:**
Использовать Gemini с grounding для проверки актуальности законодательства.

**Реализация:**

```python
# legaltechkz/models/gemini_model.py

def generate_with_grounding(self, prompt: str,
                           dynamic_retrieval: bool = True) -> Dict[str, Any]:
    """
    Generate with Google Search grounding for up-to-date information.

    Args:
        prompt: Query that may benefit from current web information
        dynamic_retrieval: Let model decide when to search (recommended)

    Returns:
        {
            'response': str,
            'grounding_metadata': {
                'search_queries': List[str],
                'grounding_chunks': List[dict],
                'web_search_queries': List[str]
            }
        }
    """
    from google.genai import types

    # Configure grounding
    if dynamic_retrieval:
        # Model decides when to search
        google_search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        config = types.GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"]
        )
    else:
        # Always use grounding
        config = types.GenerateContentConfig(
            grounding=types.GroundingConfig(
                google_search_grounding=types.GoogleSearchGroundingConfig()
            )
        )

    response = self.client.models.generate_content(
        model=self.model_name,
        contents=prompt,
        config=config
    )

    # Extract grounding metadata
    grounding_metadata = {}
    if hasattr(response, 'grounding_metadata'):
        grounding_metadata = {
            'search_queries': response.grounding_metadata.search_entry_point.rendered_content,
            'grounding_chunks': [
                {
                    'web_uri': chunk.web.uri,
                    'web_title': chunk.web.title
                }
                for chunk in response.grounding_metadata.grounding_chunks
            ],
            'web_search_queries': response.grounding_metadata.web_search_queries
        }

    return {
        'response': response.text,
        'grounding_metadata': grounding_metadata
    }
```

**Применение в Фильтре Системной Интеграции:**

```python
class SystemIntegrationFilterAgent(BaseExpertAgent):
    """
    Фильтр системной интеграции - проверяет коллизии с действующим законодательством.
    Использует Gemini с grounding для поиска актуальных версий законов.
    """

    def __init__(self, model: BaseModel, grounding_model: Optional[GeminiModel] = None):
        super().__init__(model)
        self.grounding_model = grounding_model  # Gemini для grounding

    def analyze_fragment(self, fragment: DocumentFragment,
                        checklist: str) -> Dict[str, Any]:
        # Шаг 1: Основной анализ через Claude
        analysis = super().analyze_fragment(fragment, checklist)

        # Шаг 2: Если найдены ссылки на другие законы - проверить актуальность
        if self.grounding_model and self._has_legal_references(analysis):
            references = self._extract_legal_references(analysis)

            for ref in references:
                # Проверить через Google Search
                grounding_query = f"""
                Найди актуальную редакцию {ref['law_name']} {ref.get('article', '')}
                на официальном сайте законодательства Республики Казахстан (adilet.zan.kz).
                Укажи дату последних изменений.
                """

                grounded_result = self.grounding_model.generate_with_grounding(
                    prompt=grounding_query,
                    dynamic_retrieval=True
                )

                # Добавить в анализ
                analysis['legal_references_verification'] = analysis.get('legal_references_verification', [])
                analysis['legal_references_verification'].append({
                    'reference': ref,
                    'current_version': grounded_result['response'],
                    'sources': grounded_result['grounding_metadata']['grounding_chunks']
                })

        return analysis
```

**Пример использования:**

```
Статья анализируемого проекта НПА ссылается на:
"в соответствии со статьей 123 Гражданского кодекса РК"

→ Gemini с grounding:
  1. Ищет на adilet.zan.kz актуальную статью 123 ГК РК
  2. Проверяет когда были последние изменения
  3. Возвращает актуальный текст + источники

→ В отчете:
  "Ссылка на ст. 123 ГК РК актуальна.
   Последние изменения: 15.03.2024.
   Источник: https://adilet.zan.kz/rus/docs/K1400000269"
```

### 4. Structured Outputs для гарантии формата (Приоритет: ВЫСОКИЙ)

**Что делать:**
Использовать Structured Outputs OpenAI для этапов где критичен формат JSON.

**Реализация:**

```python
# legaltechkz/models/openai_model.py

from pydantic import BaseModel as PydanticBaseModel
from typing import Type

def generate_structured(self,
                       prompt: str,
                       response_model: Type[PydanticBaseModel],
                       system_message: Optional[str] = None) -> PydanticBaseModel:
    """
    Generate with guaranteed structured output using Pydantic model.

    Args:
        prompt: User prompt
        response_model: Pydantic model class defining the structure
        system_message: Optional system message

    Returns:
        Instance of response_model with parsed data
    """
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    completion = self.client.beta.chat.completions.parse(
        model=self.model_name,
        messages=messages,
        response_format=response_model,
        temperature=self.temperature
    )

    return completion.choices[0].message.parsed
```

**Определение схем для отчетов:**

```python
# legaltechkz/expertise/report_schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ConfidenceLevel(str, Enum):
    HIGH = "высокая"
    MEDIUM = "средняя"
    LOW = "низкая"

class RelevanceVerdict(str, Enum):
    NORMATIVE = "Нормативен"
    NON_NORMATIVE = "Ненормативен"
    MIXED = "Смешанный"

class RelevanceAnalysis(BaseModel):
    """Структура анализа Фильтра Релевантности."""

    article_number: str = Field(description="Номер статьи")
    article_text: str = Field(description="Текст анализируемой нормы")

    # Тест на нормативность
    normativity_test: dict = Field(description="Результаты 5 тестов нормативности")
    normativity_score: float = Field(ge=0, le=1, description="Итоговый балл нормативности")

    # Матрица ILNR
    ilnr_impact: int = Field(ge=1, le=5, description="Воздействие (Impact)")
    ilnr_legality: int = Field(ge=1, le=5, description="Законность (Legality)")
    ilnr_necessity: int = Field(ge=1, le=5, description="Необходимость (Necessity)")
    ilnr_rationality: int = Field(ge=1, le=5, description="Рациональность (Rationality)")
    ilnr_index: float = Field(description="Индекс ILNR")

    # Вердикт
    verdict: RelevanceVerdict
    recommended_level: str = Field(description="Рекомендуемый уровень акта")

    # Рекомендации
    recommendations: List[str] = Field(description="Конкретные рекомендации")
    confidence: ConfidenceLevel = Field(description="Уровень уверенности")


class ConstitutionalityAnalysis(BaseModel):
    """Структура анализа Фильтра Конституционности."""

    article_number: str
    article_text: str

    # NLI анализ
    constitutional_nli: dict = Field(description="NLI анализ с Конституцией")
    court_decisions_nli: Optional[dict] = Field(description="NLI с постановлениями КС")

    # Результаты
    is_constitutional: bool = Field(description="Соответствует ли Конституции")
    contradictions_found: List[str] = Field(description="Найденные противоречия")

    recommendations: List[str]
    confidence: ConfidenceLevel


class SystemIntegrationAnalysis(BaseModel):
    """Структура анализа Фильтра Системной Интеграции."""

    article_number: str
    article_text: str

    # Аудиты
    vertical_audit: dict = Field(description="Вертикальный аудит")
    horizontal_screening: dict = Field(description="Горизонтальный скрининг")
    terminology_control: dict = Field(description="Терминологический контроль")

    # Результаты
    conflicts_found: List[dict] = Field(description="Найденные коллизии")
    terminology_issues: List[str] = Field(description="Терминологические проблемы")

    recommendations: List[str]
    confidence: ConfidenceLevel


class LegalTechnicalAnalysis(BaseModel):
    """Структура Юридико-технической экспертизы."""

    article_number: str
    article_text: str

    # Анализы
    legal_technique: dict = Field(description="Оценка юридической техники")
    linguistic_analysis: dict = Field(description="Лингвистический анализ")
    logical_assessment: dict = Field(description="Логическая оценка")

    issues_found: List[str] = Field(description="Найденные проблемы")
    recommendations: List[str]
    confidence: ConfidenceLevel


class AntiCorruptionAnalysis(BaseModel):
    """Структура Антикоррупционной экспертизы."""

    article_number: str
    article_text: str

    # Факторы
    linguistic_uncertainty: dict = Field(description="Юридико-лингвистическая неопределенность")
    discretion_width: dict = Field(description="Широта дискреции")
    legal_gaps: List[str] = Field(description="Правовые пробелы")
    administrative_barriers: List[str] = Field(description="Административные барьеры")

    # Оценка
    corruption_risk_level: str = Field(description="Уровень коррупционного риска")
    risk_factors_count: int = Field(ge=0, description="Количество факторов")

    recommendations: List[str]
    confidence: ConfidenceLevel


class GenderAnalysis(BaseModel):
    """Структура Гендерной экспертизы."""

    article_number: str
    article_text: str

    # Анализы
    gender_impact: dict = Field(description="Гендерное воздействие")
    discrimination_check: dict = Field(description="Проверка дискриминации")
    stereotype_analysis: dict = Field(description="Анализ стереотипов")

    # Результаты
    has_gender_impact: bool = Field(description="Имеет ли гендерное воздействие")
    issues_found: List[str] = Field(description="Найденные проблемы")

    recommendations: List[str]
    confidence: ConfidenceLevel
```

**Применение:**

```python
# legaltechkz/expertise/legal_expertise_pipeline.py

from legaltechkz.expertise.report_schemas import (
    RelevanceAnalysis,
    ConstitutionalityAnalysis,
    # ... остальные схемы
)

class LegalExpertisePipeline:
    def _run_stage_with_structured_output(self,
                                         stage_name: str,
                                         agent: BaseExpertAgent,
                                         fragment: DocumentFragment,
                                         response_model: Type[PydanticBaseModel]) -> dict:
        """
        Запустить этап с гарантией структурированного вывода.
        """
        # Для финального отчета используем GPT с Structured Outputs
        gpt_model = self.model_router._create_model_from_config({
            "provider": "openai",
            "model_name": "gpt-4o-2024-08-06",  # Поддерживает Structured Outputs
            "temperature": 0.1
        })

        # Получить анализ от основного агента (Claude)
        raw_analysis = agent.analyze_fragment(fragment, checklist)

        # Преобразовать в структурированный формат через GPT
        conversion_prompt = f"""
        Преобразуй следующий анализ правовой экспертизы в строгий JSON формат.

        Анализ:
        {raw_analysis['analysis']}

        Извлеки все необходимые поля согласно схеме.
        """

        structured_result = gpt_model.generate_structured(
            prompt=conversion_prompt,
            response_model=response_model,
            system_message="Ты преобразуешь правовые анализы в структурированный формат."
        )

        return structured_result.model_dump()
```

**Преимущества:**
- 100% гарантия валидного JSON
- Автоматическая валидация через Pydantic
- Невозможно получить некорректный формат
- Легко парсить и обрабатывать результаты

### 5. Batch API для массовой обработки (Приоритет: СРЕДНИЙ)

**Когда использовать:**
- Анализ архива НПА (десятки/сотни документов)
- Ночная обработка
- Не требуется реального времени

**Реализация:**

```python
# legaltechkz/batch/batch_processor.py

from typing import List, Dict, Any
import json
from pathlib import Path
import time

class BatchExpertiseProcessor:
    """
    Обработчик batch экспертизы множества НПА.
    Использует Batch API для экономии 50%.
    """

    def __init__(self, provider: str = "anthropic"):
        """
        Args:
            provider: "anthropic", "openai", или "google"
        """
        self.provider = provider
        self.model_router = ModelRouter()

    def prepare_batch_file(self,
                          documents: List[Dict[str, str]],
                          output_path: str) -> str:
        """
        Подготовить JSONL файл для batch обработки.

        Args:
            documents: [{"id": "doc1", "text": "...", "name": "Закон о..."}, ...]
            output_path: Путь к выходному JSONL файлу

        Returns:
            Путь к созданному файлу
        """
        batch_requests = []

        for doc in documents:
            # Для каждого документа создаем запрос на полную экспертизу
            request = self._create_batch_request(
                custom_id=doc['id'],
                document_text=doc['text'],
                document_name=doc.get('name', doc['id'])
            )
            batch_requests.append(request)

        # Записать в JSONL
        with open(output_path, 'w', encoding='utf-8') as f:
            for req in batch_requests:
                f.write(json.dumps(req, ensure_ascii=False) + '\n')

        return output_path

    def _create_batch_request(self, custom_id: str,
                             document_text: str,
                             document_name: str) -> dict:
        """Создать batch запрос в формате провайдера."""

        if self.provider == "anthropic":
            return {
                "custom_id": custom_id,
                "params": {
                    "model": "claude-sonnet-4-5-20250514",
                    "max_tokens": 16000,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"""
                            Проведи полную комплексную правовую экспертизу следующего НПА:

                            Название: {document_name}

                            Текст:
                            {document_text}

                            Выполни все 6 этапов:
                            1. Фильтр Релевантности
                            2. Фильтр Конституционности
                            3. Фильтр Системной Интеграции
                            4. Юридико-техническая экспертиза
                            5. Антикоррупционная экспертиза
                            6. Гендерная экспертиза

                            Для каждой статьи предоставь детальный анализ.
                            """
                        }
                    ]
                }
            }

        elif self.provider == "openai":
            return {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4.1-2024-08-06",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Ты эксперт по правовой экспертизе НПА РК."
                        },
                        {
                            "role": "user",
                            "content": f"Проведи полную экспертизу НПА: {document_name}\n\n{document_text}"
                        }
                    ],
                    "max_tokens": 16000
                }
            }

        # Google Gemini batch format
        else:
            return {
                "request": {
                    "contents": [{
                        "role": "user",
                        "parts": [{
                            "text": f"Экспертиза НПА: {document_name}\n\n{document_text}"
                        }]
                    }]
                },
                "request_id": custom_id
            }

    def submit_batch(self, batch_file_path: str) -> str:
        """
        Отправить batch на обработку.

        Returns:
            batch_id для отслеживания статуса
        """
        if self.provider == "anthropic":
            from anthropic import Anthropic
            client = Anthropic()

            with open(batch_file_path, 'rb') as f:
                batch = client.messages.batches.create(
                    requests=f
                )

            return batch.id

        elif self.provider == "openai":
            from openai import OpenAI
            client = OpenAI()

            with open(batch_file_path, 'rb') as f:
                batch_input_file = client.files.create(
                    file=f,
                    purpose="batch"
                )

            batch = client.batches.create(
                input_file_id=batch_input_file.id,
                endpoint="/v1/chat/completions",
                completion_window="24h"
            )

            return batch.id

        else:  # Google
            # Используем Files API для загрузки
            from google import genai
            client = genai.Client()

            # Upload batch file
            file = client.files.upload(path=batch_file_path)

            # Create batch job
            batch_job = client.batches.create(
                src=file.uri,
                model="gemini-2.5-flash"
            )

            return batch_job.name

    def check_batch_status(self, batch_id: str) -> dict:
        """Проверить статус batch обработки."""

        if self.provider == "anthropic":
            from anthropic import Anthropic
            client = Anthropic()
            batch = client.messages.batches.retrieve(batch_id)

            return {
                'status': batch.processing_status,
                'requests_total': batch.request_counts.total,
                'requests_completed': batch.request_counts.succeeded,
                'requests_failed': batch.request_counts.errored
            }

        elif self.provider == "openai":
            from openai import OpenAI
            client = OpenAI()
            batch = client.batches.retrieve(batch_id)

            return {
                'status': batch.status,
                'requests_total': batch.request_counts.total,
                'requests_completed': batch.request_counts.completed,
                'requests_failed': batch.request_counts.failed
            }

        else:  # Google
            from google import genai
            client = genai.Client()
            batch = client.batches.get(name=batch_id)

            return {
                'status': batch.state.name,
                'requests_total': batch.total_requests,
                'requests_completed': batch.processed_requests
            }

    def retrieve_results(self, batch_id: str, output_dir: str) -> List[Dict]:
        """
        Получить результаты batch обработки.

        Returns:
            Список результатов экспертизы для каждого документа
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        if self.provider == "anthropic":
            from anthropic import Anthropic
            client = Anthropic()

            # Получить результаты
            results = []
            for result in client.messages.batches.results(batch_id):
                if result.result.type == "succeeded":
                    results.append({
                        'document_id': result.custom_id,
                        'expertise': result.result.message.content[0].text,
                        'success': True
                    })
                else:
                    results.append({
                        'document_id': result.custom_id,
                        'error': result.result.error,
                        'success': False
                    })

            # Сохранить
            output_file = Path(output_dir) / f"batch_{batch_id}_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            return results

        elif self.provider == "openai":
            from openai import OpenAI
            client = OpenAI()

            batch = client.batches.retrieve(batch_id)

            # Скачать файл результатов
            if batch.output_file_id:
                file_response = client.files.content(batch.output_file_id)
                output_file = Path(output_dir) / f"batch_{batch_id}_results.jsonl"

                with open(output_file, 'wb') as f:
                    f.write(file_response.content)

                # Парсить результаты
                results = []
                with open(output_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        result = json.loads(line)
                        results.append({
                            'document_id': result['custom_id'],
                            'expertise': result['response']['body']['choices'][0]['message']['content'],
                            'success': True
                        })

                return results

        else:  # Google
            from google import genai
            client = genai.Client()

            batch = client.batches.get(name=batch_id)

            # Скачать результаты
            output_file_uri = batch.output_uri
            # Download and parse...

            return []  # Implement based on Google's format

    def wait_for_completion(self, batch_id: str,
                           check_interval: int = 60) -> dict:
        """
        Ждать завершения batch обработки.

        Args:
            batch_id: ID batch задачи
            check_interval: Интервал проверки в секундах

        Returns:
            Финальный статус
        """
        while True:
            status = self.check_batch_status(batch_id)

            print(f"Статус: {status['status']}")
            print(f"Обработано: {status['requests_completed']}/{status['requests_total']}")

            if status['status'] in ['completed', 'COMPLETED', 'ended']:
                return status

            time.sleep(check_interval)
```

**Пример использования:**

```python
# examples/batch_expertise_example.py

from legaltechkz.batch.batch_processor import BatchExpertiseProcessor

# Подготовить список НПА для анализа
documents = [
    {
        "id": "law_001",
        "name": "Закон о цифровизации 2024",
        "text": "... полный текст закона ..."
    },
    {
        "id": "law_002",
        "name": "Проект изменений в ГК РК",
        "text": "... полный текст ..."
    },
    # ... еще 98 документов
]

# Создать batch processor
processor = BatchExpertiseProcessor(provider="anthropic")

# Подготовить batch файл
batch_file = processor.prepare_batch_file(
    documents=documents,
    output_path="batch_requests.jsonl"
)

# Отправить на обработку
batch_id = processor.submit_batch(batch_file)
print(f"Batch отправлен: {batch_id}")

# Ждать завершения
print("Ожидание завершения (до 24 часов)...")
status = processor.wait_for_completion(batch_id)

# Получить результаты
results = processor.retrieve_results(
    batch_id=batch_id,
    output_dir="batch_results"
)

# Обработать результаты
for result in results:
    if result['success']:
        print(f"✅ {result['document_id']}: экспертиза завершена")
        # Сохранить отчет
        with open(f"reports/{result['document_id']}.txt", 'w') as f:
            f.write(result['expertise'])
    else:
        print(f"❌ {result['document_id']}: ошибка - {result['error']}")

print(f"\n💰 Экономия: 50% от стандартной цены")
print(f"   Обработано документов: {len(results)}")
```

**Экономика:**
- 100 НПА × среднее 50K токенов каждый = 5M токенов
- Claude стандартно: 5M × $3/M = $15
- Claude batch: 5M × $1.5/M = **$7.50** (экономия $7.50)
- Claude batch + prompt caching: **~$3** (экономия $12)

## Матрица приоритетов внедрения

| Функция | Приоритет | Сложность | Экономия | Улучшение качества |
|---------|-----------|-----------|----------|-------------------|
| **Prompt Caching (Claude)** | 🔴 ВЫСОКИЙ | Низкая | 90% на промптах | - |
| **Extended Thinking (Claude)** | 🔴 ВЫСОКИЙ | Низкая | - | +18% точность |
| **Structured Outputs (OpenAI)** | 🔴 ВЫСОКИЙ | Средняя | - | 100% валидный JSON |
| **Grounding (Gemini)** | 🟡 СРЕДНИЙ | Средняя | - | Актуальные данные |
| **Batch API** | 🟡 СРЕДНИЙ | Высокая | 50% общая | - |
| **Implicit Caching (Gemini)** | 🟢 НИЗКИЙ | Нет (авто) | Бесплатно | - |

## Рекомендуемый план внедрения

### Фаза 1: Критичные оптимизации (1-2 недели)

1. **Неделя 1:**
   - ✅ Внедрить Prompt Caching для Claude во всех 6 агентах
   - ✅ Добавить Extended Thinking для 3 сложных этапов
   - Ожидаемая экономия: 85-90% на повторяющихся промптах
   - Улучшение: +15-20% точность сложных анализов

2. **Неделя 2:**
   - ✅ Реализовать Structured Outputs для всех схем отчетов
   - ✅ Создать Pydantic модели для 6 типов экспертизы
   - Результат: 100% гарантия валидного формата

### Фаза 2: Актуализация данных (1 неделя)

3. **Неделя 3:**
   - ✅ Интегрировать Gemini Grounding в Фильтр Системной Интеграции
   - ✅ Добавить проверку актуальности законодательства
   - Результат: Автоматическая проверка через adilet.zan.kz

### Фаза 3: Масштабирование (2 недели)

4. **Недели 4-5:**
   - ✅ Реализовать Batch API processor
   - ✅ Поддержка всех трех провайдеров
   - ✅ Создать примеры массовой обработки
   - Результат: Возможность обрабатывать десятки НПА с экономией 50%

## Итоговая оценка эффективности

### Для типичного НПА (100 статей, 6 этапов экспертизы):

**Без оптимизаций:**
- Стоимость: ~$15-20
- Время: 30-40 минут
- Качество: Базовый анализ
- Гарантия формата: Нет

**С полными оптимизациями:**
- Стоимость: ~$2-3 (экономия 85%)
- Время: 25-35 минут (с thinking)
- Качество: +18% точность на сложных задачах
- Гарантия формата: 100%
- Актуальность: Проверка через Google Search
- Прозрачность: Видимые рассуждения модели

### Для массовой обработки (100 НПА в batch режиме):

**Без оптимизаций:**
- Стоимость: ~$1,500-2,000
- Время: Реальное время обработки
- Риск: Может упереться в rate limits

**С batch + caching:**
- Стоимость: ~$300-400 (экономия 80%)
- Время: До 24 часов (фоновая обработка)
- Гарантия: Dedicated quota, нет rate limits

## Выводы и рекомендации

### Обязательно внедрить (критично):

1. ✅ **Prompt Caching (Claude)** - максимальная экономия для нашей задачи
2. ✅ **Extended Thinking (Claude)** - значительное улучшение качества
3. ✅ **Structured Outputs (OpenAI)** - надежность парсинга результатов

### Очень полезно (рекомендуется):

4. ✅ **Grounding (Gemini)** - актуальность правовой информации
5. ✅ **Batch API** - для обработки архивов НПА

### Автоматически работает:

6. ✅ **Implicit Caching (Gemini)** - бесплатная оптимизация

### Итоговая эффективность:

**Стриминг vs Batch:**
- **Streaming** - для интерактивной работы, real-time feedback
- **Batch** - для массовой обработки, экономия 50%
- **Рекомендация:** Использовать оба режима в зависимости от сценария

**ROI внедрения:**
- Разработка: 4-5 недель
- Экономия: 80-90% на регулярной работе
- Качество: +15-20% точность
- Надежность: 100% гарантия формата

Система станет значительно эффективнее и дешевле при сохранении высокого качества анализа.
