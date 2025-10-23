# Система автоматического выбора моделей и Pipeline

LegalTechKZ теперь поддерживает автоматический выбор наиболее подходящей модели для задачи и совместную работу нескольких LLM через pipeline.

## Возможности моделей

### GPT-4.1 (OpenAI)
- **Контекст:** 1M токенов
- **Вывод:** 32K токенов
- **Лучше для:**
  - Быстрые ответы
  - Общие юридические запросы
  - Суммаризация результатов

### Claude Sonnet 4.5 (Anthropic)
- **Контекст:** 200K токенов (стандарт), 1M токенов (beta)
- **Вывод:** 64K токенов
- **Лучше для:**
  - Глубокий правовой анализ
  - Логические рассуждения
  - Выявление противоречий
  - Формирование экспертных заключений

### Gemini 2.5 Flash (Google)
- **Контекст:** 1M+ токенов
- **Вывод:** 65K токенов
- **Лучше для:**
  - Обработка полных текстов законов и кодексов
  - Большие документы (>150K токенов)
  - Извлечение информации из огромных контекстов

## Автоматический выбор модели

Система автоматически выбирает модель на основе:
1. **Размера контекста** - количество токенов в запросе
2. **Типа задачи** - анализ ключевых слов
3. **Предпочтений пользователя**

### Логика выбора

```python
from legaltechkz.models.model_router import ModelRouter

# Создаём роутер с автоматическим выбором
router = ModelRouter(enable_auto_selection=True)

# Простой вопрос -> GPT-4.1
model = router.select_model_for_task("Что такое НПА?")

# Задача на рассуждение -> Claude Sonnet 4.5
model = router.select_model_for_task(
    "Проанализируй правовые последствия применения статьи 123"
)

# Большой документ -> Gemini 2.5 Flash
model = router.select_model_for_task(
    "Вот полный текст закона...",
    context=full_law_text  # >150K токенов
)
```

### Типы задач

TaskClassifier определяет тип задачи по ключевым словам:

- **large_document**: закон, кодекс, статья, полный текст, документ
- **reasoning**: анализ, рассуждение, объясни, почему, сравни, план
- **quick_response**: что такое, определение, краткий, быстро
- **general**: всё остальное

## Pipeline: совместная работа моделей

Pipeline позволяет последовательно обрабатывать данные через разные модели.

### Готовые pipeline

#### 1. Legal Analysis Pipeline

Полная правовая экспертиза:

```python
from legaltechkz.models.model_pipeline import create_legal_pipeline

pipeline = create_legal_pipeline()

result = pipeline.execute(
    initial_input="Полный текст статьи или закона...",
    return_all_outputs=True
)

print(result['final_output'])
```

**Этапы:**
1. **Обработка документа (Gemini)** - извлечение ключевых положений
2. **Правовой анализ (Claude)** - детальный анализ и рассуждения
3. **Формирование ответа (GPT-4.1)** - краткий итоговый ответ

#### 2. Document Q&A Pipeline

Вопросы-ответы по большому документу:

```python
from legaltechkz.models.model_pipeline import create_qa_pipeline

pipeline = create_qa_pipeline()

result = pipeline.execute(
    initial_input=document_text,
    template_vars={
        "question": "Какие штрафы предусмотрены?",
        "document": document_text
    },
    return_all_outputs=True
)
```

**Этапы:**
1. **Индексация (Gemini)** - поиск релевантных разделов
2. **Генерация ответа (Claude)** - детальный обоснованный ответ
3. **Форматирование (GPT-4.1)** - структурированный финальный ответ

### Создание собственного pipeline

```python
from legaltechkz.models.model_pipeline import ModelPipeline

pipeline = ModelPipeline()

# Добавляем этапы
pipeline.add_stage(
    name="Извлечение данных",
    stage_type="document_processing",  # Gemini
    prompt_template="Извлеки ключевую информацию из: {input}"
)

pipeline.add_stage(
    name="Анализ",
    stage_type="analysis",  # Claude
    prompt_template="Проанализируй: {input}"
)

pipeline.add_stage(
    name="Ответ",
    stage_type="summarization",  # GPT-4.1
    prompt_template="Сформулируй краткий ответ: {input}"
)

# Выполнение
result = pipeline.execute(initial_input="...")
```

## Конфигурация

В `config.yaml`:

```yaml
models:
  # Включить автоматический выбор
  auto_selection:
    enabled: true

  # Pipeline
  pipeline:
    enabled: true
    default_pipeline: "legal_analysis"
```

## API ключи

Установите переменные окружения:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
```

## Примеры использования

Запустите примеры:

```bash
python examples/multi_model_example.py
```

## Преимущества

✅ **Оптимизация затрат** - каждая модель для своей задачи
✅ **Лучшее качество** - используются сильные стороны каждой модели
✅ **Большие контексты** - Gemini обрабатывает документы до 1M+ токенов
✅ **Глубокий анализ** - Claude для сложных рассуждений
✅ **Быстрые ответы** - GPT-4.1 для финализации

## Технические детали

### TaskClassifier

Классифицирует задачи на основе:
- Оценки количества токенов (эвристика: 4 символа = 1 токен для английского, 2 для русского)
- Анализа ключевых слов в запросе
- Размера дополнительного контекста

### ModelRouter

Управляет:
- Регистрацией моделей
- Автоматическим выбором
- Созданием экземпляров моделей
- Fallback логикой

### ModelPipeline

Обеспечивает:
- Последовательное выполнение этапов
- Передачу данных между моделями
- Логирование и историю выполнения
- Обработку ошибок

## Мониторинг

Pipeline сохраняет историю выполнения:

```python
# Получить историю последних выполнений
history = pipeline.get_execution_history(limit=5)

for record in history:
    print(f"Дата: {record['start_time']}")
    for stage in record['stages']:
        print(f"  Этап: {stage['stage_name']}")
        print(f"  Модель: {stage['model']}")
        print(f"  Статус: {'✅' if stage['success'] else '❌'}")
```

## Отладка

Включите подробное логирование:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Это покажет:
- Какая модель выбрана и почему
- Этапы выполнения pipeline
- Размеры входных/выходных данных
- Ошибки и предупреждения
