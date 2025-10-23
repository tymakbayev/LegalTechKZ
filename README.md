# Система правовой экспертизы НПА РК

Адаптация фреймворка ANUS для проведения правовой экспертизы нормативно-правовых актов Республики Казахстан с использованием официального ресурса **adilet.zan.kz**.

## Содержание

- [Описание](#описание)
- [Возможности](#возможности)
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Примеры использования](#примеры-использования)
- [Конфигурация](#конфигурация)
- [Архитектура](#архитектура)
- [API Reference](#api-reference)

## Описание

Система правовой экспертизы - это специализированное решение на базе ANUS AI для автоматизированного анализа нормативно-правовых актов Республики Казахстан. Система работает **исключительно** с официальным ресурсом **adilet.zan.kz**, обеспечивая максимальную точность и консистентность данных.

### Ключевые особенности

- **Целевой поиск**: Поиск НПА только на adilet.zan.kz
- **Поэтапный анализ**: Структурированная проверка документов
- **Выявление противоречий**: Автоматическое обнаружение коллизий между НПА
- **Валидация ссылок**: Проверка корректности ссылок на другие документы
- **Экспертное заключение**: Формирование детального отчета

## Возможности

### 1. Поиск НПА на adilet.zan.kz

- Поиск по названию, номеру, дате
- Фильтрация по типу документа (закон, кодекс, указ, постановление, приказ)
- Фильтрация по статусу (действующий/утративший силу)
- Фильтрация по году принятия

### 2. Проверка консистентности

- Анализ структуры документа
- Проверка последовательности нумерации статей
- Анализ терминологии
- Выявление устаревших формулировок

### 3. Валидация ссылок

- Проверка полноты ссылок на другие НПА
- Валидация формата ссылок
- Опциональная онлайн-проверка доступности документов

### 4. Выявление противоречий

- Сравнение определений терминов
- Выявление коллизий между документами
- Анализ процедур и норм

### 5. Формирование экспертного заключения

- Оценка качества документа
- Список критических замечаний
- Рекомендации по доработке
- Итоговое заключение о готовности к принятию

## Установка

### Требования

- Python 3.11+
- pip
- Git

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/nikmcfly/ANUS.git
cd ANUS
```

### Шаг 2: Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установка зависимостей
pip install -e .
pip install requests beautifulsoup4 pyyaml
```

### Шаг 3: Настройка конфигурации

```bash
# Копируем конфигурацию для правовой экспертизы
cp config_legal_expert.yaml config.yaml

# Устанавливаем API ключ для LLM (OpenAI/Anthropic)
export OPENAI_API_KEY="your_api_key_here"
# или
export ANTHROPIC_API_KEY="your_api_key_here"
```

## Быстрый старт

### Простой поиск НПА

```python
from anus.tools.adilet_search import AdiletSearchTool

# Создаем инструмент поиска
search_tool = AdiletSearchTool()

# Ищем закон
result = search_tool.execute(
    query="Налоговый кодекс",
    doc_type="code",
    status="active"
)

print(f"Найдено документов: {result['result_count']}")
for doc in result['results']:
    print(f"- {doc['title']}")
    print(f"  URL: {doc['url']}")
```

### Проверка консистентности документа

```python
from anus.tools.legal_analysis import LegalConsistencyChecker
from anus.tools.adilet_search import AdiletDocumentFetcher

# Получаем документ
fetcher = AdiletDocumentFetcher()
doc_result = fetcher.execute(url="https://adilet.zan.kz/rus/docs/example")
document = doc_result['document']

# Проверяем консистентность
checker = LegalConsistencyChecker()
consistency = checker.execute(
    document_text=document['text'],
    document_metadata={
        "title": document['title'],
        "number": document['number'],
        "date": document['date']
    }
)

print(f"Качество документа: {consistency['overall_assessment']['quality']}")
print(f"Критических замечаний: {consistency['overall_assessment']['issues_count']}")
print(f"Предупреждений: {consistency['overall_assessment']['warnings_count']}")
```

### Полная правовая экспертиза

```python
from anus.agents.legal_expert_agent import LegalExpertAgent

# Создаем агента
agent = LegalExpertAgent(name="legal_expert")

# Выполняем полную экспертизу
result = agent.execute(
    task="Провести полную правовую экспертизу Налогового кодекса РК"
)

# Получаем экспертное заключение
conclusion = result['expert_conclusion']

print(f"Документ: {conclusion['document']['title']}")
print(f"Качество: {conclusion['quality_assessment']}")
print(f"Готов к принятию: {conclusion['ready_for_approval']}")
print(f"\nИтоговое заключение: {conclusion['final_verdict']}")

# Выводим критические замечания
if conclusion['critical_issues']:
    print("\nКритические замечания:")
    for issue in conclusion['critical_issues']:
        print(f"- [{issue['severity']}] {issue['description']}")

# Выводим рекомендации
if conclusion['recommendations']:
    print("\nРекомендации:")
    for rec in conclusion['recommendations']:
        print(f"- {rec}")
```

## Примеры использования

### Пример 1: Поиск и анализ закона

```python
from anus.agents.legal_expert_agent import LegalExpertAgent

agent = LegalExpertAgent()

# Поиск и анализ
result = agent.execute(
    task='Найти и проанализировать "Закон о государственных закупках"'
)

print(result['summary'])
```

### Пример 2: Сравнение двух НПА

```python
from anus.tools.adilet_search import AdiletSearchTool, AdiletDocumentFetcher
from anus.tools.legal_analysis import LegalContradictionDetector

# Получаем два документа
search = AdiletSearchTool()
fetcher = AdiletDocumentFetcher()

# Первый документ
result1 = search.execute(query="Гражданский кодекс")
doc1_url = result1['results'][0]['url']
doc1 = fetcher.execute(url=doc1_url)['document']

# Второй документ
result2 = search.execute(query="Семейный кодекс")
doc2_url = result2['results'][0]['url']
doc2 = fetcher.execute(url=doc2_url)['document']

# Выявляем противоречия
detector = LegalContradictionDetector()
contradictions = detector.execute(
    document1=doc1,
    document2=doc2,
    scope="definitions"
)

print(f"Найдено противоречий: {contradictions['contradictions_count']}")
for contra in contradictions['contradictions']:
    print(f"\nТермин: {contra['term']}")
    print(f"В {doc1['title']}: {contra['definition1']}")
    print(f"В {doc2['title']}: {contra['definition2']}")
```

### Пример 3: Командная строка

```bash
# Поиск документа
python -m anus.cli legal-search "Трудовой кодекс" --type=code

# Полная экспертиза
python -m anus.cli legal-examine "Закон о государственной службе"

# Анализ консистентности
python -m anus.cli legal-check --url="https://adilet.zan.kz/rus/docs/..."

# Сравнение документов
python -m anus.cli legal-compare \
    --doc1="Закон о защите прав потребителей" \
    --doc2="Гражданский кодекс"
```

### Пример 4: Пакетная обработка

```python
from anus.agents.legal_expert_agent import LegalExpertAgent
import json

agent = LegalExpertAgent()

# Список документов для проверки
documents = [
    "Налоговый кодекс",
    "Трудовой кодекс",
    "Гражданский кодекс"
]

results = []

for doc_name in documents:
    print(f"Проверяю: {doc_name}")

    result = agent.execute(
        task=f"Провести проверку консистентности {doc_name}"
    )

    results.append({
        "document": doc_name,
        "quality": result['consistency_result']['overall_assessment']['quality'],
        "score": result['consistency_result']['overall_assessment']['score'],
        "issues": result['consistency_result']['overall_assessment']['issues_count']
    })

# Сохраняем результаты
with open("examination_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nРезультаты проверки:")
for r in results:
    print(f"{r['document']}: {r['quality']} (оценка: {r['score']}, замечаний: {r['issues']})")
```

## Конфигурация

Конфигурация системы находится в файле `config_legal_expert.yaml`. Основные параметры:

### Настройки агента

```yaml
agent:
  name: "legal_expert_kz"
  mode: "single"  # или "multi" для мультиагентного режима
  max_iterations: 20
```

### Настройки поиска на adilet.zan.kz

```yaml
tools:
  adilet_search:
    base_url: "https://adilet.zan.kz"
    search_timeout: 15
    max_results: 10
    retry_attempts: 3
```

### Настройки проверки консистентности

```yaml
tools:
  check_consistency:
    check_references: true
    check_structure: true
    check_terminology: true
    strict_mode: false
```

### Критерии для одобрения документа

```yaml
legal_examination:
  approval_criteria:
    max_critical_issues: 0
    max_warnings: 3
    min_quality_score: 80
    require_valid_references: true
```

## Архитектура

### Компоненты системы

```
anus/
├── tools/
│   ├── adilet_search.py          # Поиск на adilet.zan.kz
│   └── legal_analysis.py          # Инструменты анализа
├── agents/
│   └── legal_expert_agent.py      # Агент правовой экспертизы
└── config_legal_expert.yaml       # Конфигурация
```

### Процесс экспертизы

1. **Поиск документа** на adilet.zan.kz
2. **Получение полного текста** документа
3. **Проверка консистентности**:
   - Структура документа
   - Нумерация статей
   - Терминология
4. **Валидация ссылок** на другие НПА
5. **Поиск связанных документов**
6. **Формирование заключения**

## API Reference

### AdiletSearchTool

**Метод:** `execute(query, doc_type="all", year=None, status="active")`

**Параметры:**
- `query` (str): Поисковый запрос
- `doc_type` (str): Тип документа ("law", "code", "decree", "resolution", "order", "all")
- `year` (str, optional): Год принятия
- `status` (str): Статус ("active", "invalid", "all")

**Возвращает:** Словарь с результатами поиска

### LegalConsistencyChecker

**Метод:** `execute(document_text, document_metadata=None, check_references=True, check_structure=True)`

**Параметры:**
- `document_text` (str): Текст документа
- `document_metadata` (dict, optional): Метаданные документа
- `check_references` (bool): Проверять ссылки
- `check_structure` (bool): Проверять структуру

**Возвращает:** Словарь с результатами проверки

### LegalContradictionDetector

**Метод:** `execute(document1, document2, scope="all")`

**Параметры:**
- `document1` (dict): Первый документ
- `document2` (dict): Второй документ
- `scope` (str): Область проверки ("all", "definitions", "norms", "procedures")

**Возвращает:** Словарь с выявленными противоречиями

### LegalExpertAgent

**Метод:** `execute(task, **kwargs)`

**Параметры:**
- `task` (str): Описание задачи
- `**kwargs`: Дополнительные параметры

**Возвращает:** Словарь с результатами выполнения задачи

## Ограничения доменов

**ВАЖНО:** Система настроена на работу **ИСКЛЮЧИТЕЛЬНО** с adilet.zan.kz для обеспечения консистентности и точности данных.

Конфигурация безопасности:

```yaml
security:
  allowed_domains:
    - "adilet.zan.kz"
    - "zan.kz"
  block_external_domains: true
```

## Поддержка

Для вопросов и предложений создавайте issues в репозитории GitHub.

## Лицензия

MIT License - см. файл LICENSE в корне репозитория.

---

**Разработано на базе ANUS AI Framework**
Адаптировано для правовой экспертизы НПА Республики Казахстан
