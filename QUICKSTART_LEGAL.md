# Быстрый старт: Система правовой экспертизы НПА РК

## Установка за 5 минут

### 1. Клонирование репозитория

```bash
git clone https://github.com/nikmcfly/LegalTechKZ.git
cd LegalTechKZ
```

### 2. Установка зависимостей

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
pip install requests beautifulsoup4 pyyaml
```

### 3. Настройка

```bash
# Копируем конфигурацию
cp config_legal_expert.yaml config.yaml

# Устанавливаем API ключ
export OPENAI_API_KEY="ваш_ключ"
```

## Первый запуск

### Запуск демо

```bash
python examples/legal_expert_demo.py
```

### Простой пример в коде

```python
from legaltechkz.tools.adilet_search import AdiletSearchTool

# Поиск закона
search = AdiletSearchTool()
result = search.execute(query="Налоговый кодекс", doc_type="code")

print(f"Найдено: {result['result_count']} документов")
for doc in result['results']:
    print(f"- {doc['title']}")
    print(f"  {doc['url']}")
```

### Полная экспертиза

```python
from legaltechkz.agents.legal_expert_agent import LegalExpertAgent

agent = LegalExpertAgent()
result = agent.execute(
    task="Провести полную экспертизу Трудового кодекса РК"
)

conclusion = result['expert_conclusion']
print(f"Качество: {conclusion['quality_assessment']}")
print(f"Заключение: {conclusion['final_verdict']}")
```

## Основные команды

### Поиск документа

```python
from legaltechkz.tools.adilet_search import AdiletSearchTool

search = AdiletSearchTool()
result = search.execute(
    query="название документа",
    doc_type="law",  # law, code, decree, resolution, order
    status="active"   # active, invalid, all
)
```

### Проверка консистентности

```python
from legaltechkz.tools.legal_analysis import LegalConsistencyChecker

checker = LegalConsistencyChecker()
result = checker.execute(
    document_text="текст документа",
    check_references=True,
    check_structure=True
)
```

### Сравнение документов

```python
from legaltechkz.tools.legal_analysis import LegalContradictionDetector

detector = LegalContradictionDetector()
result = detector.execute(
    document1={"title": "...", "text": "..."},
    document2={"title": "...", "text": "..."},
    scope="all"  # all, definitions, norms, procedures
)
```

## Структура результатов

### Результат поиска

```python
{
    "status": "success",
    "query": "Налоговый кодекс",
    "result_count": 1,
    "results": [
        {
            "title": "Кодекс Республики Казахстан...",
            "url": "https://adilet.zan.kz/rus/docs/...",
            "number": "99-V",
            "date": "10.12.2008",
            "status": "Действует"
        }
    ],
    "source": "adilet.zan.kz"
}
```

### Результат проверки консистентности

```python
{
    "status": "success",
    "overall_assessment": {
        "quality": "Отлично",
        "score": 95,
        "ready_for_approval": True,
        "issues_count": 0,
        "warnings_count": 2
    },
    "issues": [],
    "warnings": [
        {"type": "...", "message": "..."}
    ],
    "recommendations": [
        "Рекомендация 1",
        "Рекомендация 2"
    ]
}
```

### Экспертное заключение

```python
{
    "document": {
        "title": "...",
        "number": "...",
        "date": "..."
    },
    "quality_assessment": "Отлично",
    "score": 95,
    "ready_for_approval": True,
    "critical_issues": [],
    "warnings": [],
    "recommendations": [],
    "final_verdict": "Документ соответствует требованиям..."
}
```

## Частые вопросы

### Q: Как добавить свои критерии проверки?

A: Отредактируйте `config_legal_expert.yaml`:

```yaml
legal_examination:
  approval_criteria:
    max_critical_issues: 0
    max_warnings: 3
    min_quality_score: 80
```

### Q: Как изменить строгость проверки?

A: В конфигурации:

```yaml
tools:
  check_consistency:
    strict_mode: true  # Строгий режим
```

### Q: Как сохранить результаты?

A: Используйте встроенное автосохранение:

```yaml
advanced:
  auto_save_results: true
  results_path: "./results/legal_examinations"
```

Или вручную:

```python
import json

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

## Ограничения

**ВАЖНО:** Система работает ТОЛЬКО с adilet.zan.kz

- Поиск выполняется только на adilet.zan.kz
- Блокируются запросы к другим доменам
- Обеспечивается максимальная консистентность данных

## Следующие шаги

1. Прочитайте полную документацию: `LEGAL_EXPERT_README.md`
2. Изучите примеры: `examples/legal_expert_demo.py`
3. Настройте конфигурацию: `config_legal_expert.yaml`
4. Адаптируйте под ваши требования

## Получение помощи

- GitHub Issues: https://github.com/nikmcfly/LegalTechKZ/issues
- Документация: `LEGAL_EXPERT_README.md`
- Примеры: `examples/`

---

**Готово! Начинайте работу с правовой экспертизой НПА РК**
