# Система правовой экспертизы НПА

Комплексная система для проведения многоэтапной правовой экспертизы проектов нормативных правовых актов (НПА) Республики Казахстан.

## Проблема

При ручном анализе больших документов НПА нейросети часто **пропускают статьи и пункты**, что делает экспертизу неполной. Даже при поэтапном вводе промптов некоторые части документа могут быть упущены.

## Решение

Система LegalTechKZ гарантирует **полноту анализа** через:

1. **Автоматическое разбиение** документа на структурные элементы
2. **Оглавление-чеклист** для контроля обработки каждой статьи
3. **Валидация полноты** после каждого этапа
4. **Использование Gemini 2.5 Flash** для обработки больших документов (1M+ токенов)

## Архитектура

### 1. Document Parser

Разбивает НПА на структурированные элементы:

```python
from legaltechkz.expertise.document_parser import NPADocumentParser

parser = NPADocumentParser()
fragments = parser.parse(document_text)

# Получить статистику
stats = parser.get_fragment_stats()
# {
#   'total_fragments': 45,
#   'chapters': 3,
#   'articles': 15,
#   'paragraphs': 27,
#   'article_numbers': ['1', '2', '3', ...]
# }

# Получить оглавление
toc = parser.get_table_of_contents()
# ['Статья 1: Предмет регулирования', 'Статья 2: Основные понятия', ...]
```

### 2. Completeness Validator

Гарантирует обработку всех статей:

```python
from legaltechkz.expertise.completeness_validator import CompletenessValidator

validator = CompletenessValidator(fragments)

# Пометить статью как проанализированную
validator.mark_analyzed("1", analysis_data)

# Проверить полноту
if not validator.is_complete():
    missing = validator.get_missing_articles()
    print(f"Пропущено статей: {[a.number for a in missing]}")

# Получить отчёт
report = validator.get_completion_report()
# {
#   'total_articles': 15,
#   'analyzed_articles': 15,
#   'missing_articles': 0,
#   'completion_rate': 1.0,
#   'completion_percentage': '100.0%',
#   'is_complete': True
# }
```

### 3. Шесть экспертных агентов

Каждый агент реализует свой тип экспертизы:

#### 1. Фильтр Релевантности (RelevanceFilterAgent)
- Определяет необходимость государственно-правового регулирования
- Адекватный уровень регулирования (Закон, Подзаконный акт, Soft Law)
- Выявляет ненормативные положения
- **Модель:** Claude Sonnet 4.5

#### 2. Фильтр Конституционности (ConstitutionalityFilterAgent)
- Проверяет соответствие Конституции РК
- Анализирует соответствие постановлениям Конституционного Суда
- NLI-анализ (Contradiction/Entailment/Neutral)
- **Модель:** Claude Sonnet 4.5

#### 3. Фильтр Системной Интеграции (SystemIntegrationFilterAgent)
- Вертикальный аудит (коллизии с вышестоящими актами)
- Горизонтальный скрининг (коллизии с равнозначными актами)
- Терминологический контроль
- **Модель:** Claude Sonnet 4.5

#### 4. Юридико-техническая Экспертиза (LegalTechnicalExpertAgent)
- Проверка юридической техники и структуры
- Лингвистический анализ (лексика, грамматика, стиль)
- Логическая оценка (структура «если — то — иначе»)
- **Модель:** Claude Sonnet 4.5

#### 5. Антикоррупционная Экспертиза (AntiCorruptionExpertAgent)
- Выявление юридико-лингвистической неопределённости
- Широта дискреционных полномочий
- Правовые пробелы и административные барьеры
- **Модель:** Claude Sonnet 4.5

#### 6. Гендерная Экспертиза (GenderExpertAgent)
- Оценка гендерного воздействия
- Прямая и косвенная дискриминация
- Гендерные стереотипы
- **Модель:** Claude Sonnet 4.5

### 4. Legal Expertise Pipeline

Координирует все этапы экспертизы:

```python
from legaltechkz.expertise.legal_expertise_pipeline import LegalExpertisePipeline

# Создать pipeline
pipeline = LegalExpertisePipeline()

# Провести полную экспертизу
report = pipeline.conduct_full_expertise(document_text)

if report['success']:
    print(f"Проанализировано статей: {report['total_articles_analyzed']}")
    print(f"Завершённость: {report['completeness']['completion_percentage']}")

    if report['completeness']['is_complete']:
        print("✅ Все статьи обработаны")
    else:
        print(f"⚠️ Пропущено: {report['completeness']['missing_article_numbers']}")
```

## Использование моделей

### Автоматический выбор

Pipeline автоматически выбирает модель для каждого этапа:

- **Gemini 2.5 Flash** (1M+ токенов) - для начальной обработки больших документов
- **Claude Sonnet 4.5** (64K вывод) - для всех 6 этапов экспертизы
- **GPT-4.1** - для финальной суммаризации результатов

### Обработка больших документов

Для документов > 150K токенов:

1. Gemini обрабатывает весь документ сразу (до 1M+ токенов)
2. Создаётся структурированный чеклист всех статей
3. Claude проводит детальный анализ каждой статьи
4. Validator проверяет что ничего не пропущено

## Примеры использования

### Полная комплексная экспертиза

```python
from legaltechkz.expertise.legal_expertise_pipeline import LegalExpertisePipeline

# Загрузить текст НПА
with open('project_npa.txt', 'r', encoding='utf-8') as f:
    document_text = f.read()

# Создать pipeline
pipeline = LegalExpertisePipeline()

# Запустить все 6 этапов экспертизы
report = pipeline.conduct_full_expertise(document_text)

# Проверить результаты
if report['success']:
    completeness = report['completeness']

    if completeness['is_complete']:
        print("✅ ЭКСПЕРТИЗА ПОЛНАЯ")
        print(f"   Всего статей: {completeness['total_articles']}")
        print(f"   Все обработаны: {completeness['analyzed_articles']}")
    else:
        print("⚠️ ЭКСПЕРТИЗА НЕПОЛНАЯ")
        print(f"   Пропущено: {completeness['missing_article_numbers']}")

    # Сохранить отчёт
    import json
    with open('expertise_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
```

### Выборочная экспертиза

```python
# Провести только антикоррупционную и гендерную экспертизу
skip_stages = [
    "Фильтр Релевантности",
    "Фильтр Конституционности",
    "Фильтр Системной Интеграции",
    "Юридико-техническая Экспертиза"
]

report = pipeline.conduct_full_expertise(
    document_text,
    skip_stages=skip_stages
)
```

### Анализ одной статьи

```python
from legaltechkz.expertise.expert_agents import AntiCorruptionExpertAgent
from legaltechkz.models.model_router import ModelRouter

# Выбрать модель
router = ModelRouter(enable_auto_selection=True)
model = router.select_model_for_pipeline_stage("analysis")

# Создать агента
agent = AntiCorruptionExpertAgent(model)

# Проанализировать статью
from legaltechkz.expertise.document_parser import DocumentFragment

fragment = DocumentFragment(
    type='article',
    number='5',
    title='Права и обязанности',
    text='Статья 5. Права и обязанности пользователей...',
    full_path='Статья 5',
    parent_number=None,
    char_start=0,
    char_end=100
)

result = agent.analyze_fragment(fragment, checklist="")

print(result['analysis'])
```

## Формат вывода

Каждый агент возвращает структурированный анализ:

```
* АНАЛИЗ НОРМЫ: 5
    * Текст анализируемой нормы: «...»
    * [Специфичные для агента поля]
    * Рекомендации: [Конкретные рекомендации]
    * Уровень уверенности: [0.0 до 1.0]
```

## Гарантии полноты

Система гарантирует полноту через:

1. **Шаг 0: Формирование оглавления-чеклиста**
   - Перед анализом создаётся полный список всех статей
   - Каждая статья получает уникальный ID

2. **Постатейный анализ**
   - Каждая статья анализируется отдельно
   - После анализа статья помечается как обработанная

3. **Валидация после каждого этапа**
   - Validator проверяет что все статьи обработаны
   - Если статьи пропущены - система предупреждает

4. **Итоговая проверка**
   - В конце формируется отчёт о полноте
   - Указываются пропущенные статьи (если есть)

## API ключи

Для работы системы требуются API ключи:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
```

## Запуск примера

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить пример
python examples/legal_expertise_example.py
```

## Преимущества

✅ **Гарантия полноты** - ни одна статья не будет пропущена
✅ **Автоматизация** - полная экспертиза одной командой
✅ **Структурированность** - чёткий формат вывода для каждого типа экспертизы
✅ **Масштабируемость** - обработка документов любого размера
✅ **Прозрачность** - отчёт о полноте анализа
✅ **Методологичность** - следование установленным алгоритмам экспертизы

## Ограничения

⚠️ **Требуется доступ к API** трёх провайдеров LLM
⚠️ **Время выполнения** зависит от размера документа и количества статей
⚠️ **Качество анализа** зависит от качества промптов и возможностей моделей

## Дальнейшее развитие

- Параллельная обработка статей для ускорения
- Интеграция с базой законодательства РК
- Автоматическое формирование заключений
- Веб-интерфейс для экспертизы
- Экспорт отчётов в PDF/DOCX

## Техническая поддержка

При возникновении проблем см.:
- `docs/MULTI_MODEL_SYSTEM.md` - документация по multi-model системе
- `examples/legal_expertise_example.py` - примеры использования
- Логи в консоли для отладки
