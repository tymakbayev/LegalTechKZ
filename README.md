# 🏛️ LegalTechKZ - Система правовой экспертизы НПА РК

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/AI-Powered-orange.svg" alt="AI Powered">
  <img src="https://img.shields.io/badge/Status-Beta-yellow.svg" alt="Status">
</p>

<p align="center">
  <strong>AI-powered система для автоматизированной правовой экспертизы нормативно-правовых актов Республики Казахстан</strong>
</p>

<p align="center">
  🔍 Поиск на adilet.zan.kz • 📊 Анализ консистентности • ⚖️ Выявление противоречий • 📝 Экспертные заключения
</p>

---

## 📋 Содержание

- [Описание](#описание)
- [Возможности](#возможности)
- [Быстрый старт](#быстрый-старт)
- [Установка](#установка)
- [Примеры использования](#примеры-использования)
- [Архитектура](#архитектура)
- [Конфигурация](#конфигурация)
- [API Reference](#api-reference)
- [Дорожная карта](#дорожная-карта)
- [Вклад в проект](#вклад-в-проект)
- [Лицензия](#лицензия)

## 🎯 Описание

**LegalTechKZ** - это специализированная AI-система для проведения правовой экспертизы нормативно-правовых актов Республики Казахстан. Система разработана на базе фреймворка ANUS и работает **исключительно** с официальным ресурсом **adilet.zan.kz**, обеспечивая максимальную точность и консистентность данных.

### Для кого этот проект?

- 👨‍⚖️ **Юристов** - автоматизация анализа законодательства
- 🏛️ **Государственных органов** - проверка проектов НПА
- 🎓 **Исследователей** - анализ правовых коллизий
- 💼 **Юридических компаний** - ускорение правовой экспертизы
- 👨‍💻 **Разработчиков LegalTech** - готовая база для интеграции

## ✨ Возможности

### 🔍 Поиск НПА

- Поиск по названию, номеру, дате принятия
- Фильтрация по типу документа (закон, кодекс, указ, постановление, приказ)
- Фильтрация по статусу (действующий/утративший силу)
- Фильтрация по году принятия
- **Работает только с adilet.zan.kz** - официальным источником

### 📊 Проверка консистентности

- ✅ Анализ структуры документа (главы, статьи, параграфы)
- ✅ Проверка последовательности нумерации
- ✅ Валидация ссылок на другие НПА
- ✅ Анализ терминологии
- ✅ Выявление устаревших формулировок

### ⚖️ Выявление противоречий

- Сравнение определений терминов между НПА
- Обнаружение коллизий в правовых нормах
- Анализ процедур на противоречивость
- Формирование отчета о противоречиях

### 📝 Экспертные заключения

- Комплексная оценка качества документа (балл 0-100)
- Список критических замечаний
- Предупреждения и рекомендации
- Итоговое заключение о готовности к принятию
- Детальные находки по всем проверкам

## 🚀 Быстрый старт

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/tymakbayev/LegalTechKZ.git
cd LegalTechKZ

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
pip install -e .

# Настройка API ключа
export OPENAI_API_KEY="ваш_ключ_openai"
# или
export ANTHROPIC_API_KEY="ваш_ключ_anthropic"
```

### Первый запуск

```bash
# Запуск интерактивной демонстрации
python examples/legal_expert_demo.py
```

### Простой пример

```python
from anus.tools.adilet_search import AdiletSearchTool

# Поиск закона
search = AdiletSearchTool()
result = search.execute(
    query="Налоговый кодекс",
    doc_type="code",
    status="active"
)

print(f"Найдено: {result['result_count']} документов")
for doc in result['results']:
    print(f"- {doc['title']}")
    print(f"  URL: {doc['url']}")
```

## 📖 Примеры использования

### Поиск и анализ документа

```python
from anus.agents.legal_expert_agent import LegalExpertAgent

# Создаем агента
agent = LegalExpertAgent()

# Выполняем поиск и анализ
result = agent.execute(
    task='Найти и проанализировать "Закон о государственных закупках"'
)

print(result['summary'])
```

### Полная правовая экспертиза

```python
from anus.agents.legal_expert_agent import LegalExpertAgent

agent = LegalExpertAgent()

# Полная экспертиза с заключением
result = agent.execute(
    task="Провести полную правовую экспертизу Трудового кодекса РК"
)

# Получаем экспертное заключение
conclusion = result['expert_conclusion']

print(f"Документ: {conclusion['document']['title']}")
print(f"Качество: {conclusion['quality_assessment']}")
print(f"Оценка: {conclusion['score']}/100")
print(f"Готов к принятию: {conclusion['ready_for_approval']}")
print(f"\nЗаключение: {conclusion['final_verdict']}")

# Критические замечания
if conclusion['critical_issues']:
    print("\nКритические замечания:")
    for issue in conclusion['critical_issues']:
        print(f"- [{issue['severity']}] {issue['description']}")

# Рекомендации
if conclusion['recommendations']:
    print("\nРекомендации:")
    for rec in conclusion['recommendations']:
        print(f"- {rec}")
```

### Сравнение двух НПА

```python
from anus.tools.adilet_search import AdiletSearchTool, AdiletDocumentFetcher
from anus.tools.legal_analysis import LegalContradictionDetector

# Получаем два документа
search = AdiletSearchTool()
fetcher = AdiletDocumentFetcher()

# Первый документ
result1 = search.execute(query="Гражданский кодекс")
doc1 = fetcher.execute(url=result1['results'][0]['url'])['document']

# Второй документ
result2 = search.execute(query="Семейный кодекс")
doc2 = fetcher.execute(url=result2['results'][0]['url'])['document']

# Выявляем противоречия
detector = LegalContradictionDetector()
contradictions = detector.execute(
    document1=doc1,
    document2=doc2,
    scope="definitions"
)

print(f"Найдено противоречий: {contradictions['contradictions_count']}")
```

### Пакетная обработка

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
        task=f"Проверить консистентность {doc_name}"
    )

    results.append({
        "document": doc_name,
        "quality": result['consistency_result']['overall_assessment']['quality'],
        "score": result['consistency_result']['overall_assessment']['score']
    })

# Сохраняем результаты
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

## 🏗️ Архитектура

### Структура проекта

```
LegalTechKZ/
├── anus/
│   ├── tools/
│   │   ├── adilet_search.py          # Поиск на adilet.zan.kz
│   │   └── legal_analysis.py          # Инструменты анализа НПА
│   ├── agents/
│   │   └── legal_expert_agent.py      # Агент правовой экспертизы
│   ├── core/                          # Ядро системы
│   ├── models/                        # LLM модели
│   └── ui/                            # Интерфейс
├── examples/
│   └── legal_expert_demo.py           # Демонстрационный скрипт
├── config.yaml                        # Конфигурация
├── requirements.txt                   # Зависимости
└── README.md                          # Документация
```

### Компоненты системы

**1. Инструменты поиска (Search Tools)**
- `AdiletSearchTool` - поиск НПА на adilet.zan.kz
- `AdiletDocumentFetcher` - получение полных текстов

**2. Инструменты анализа (Analysis Tools)**
- `LegalConsistencyChecker` - проверка консистентности
- `LegalContradictionDetector` - выявление противоречий
- `LegalReferenceValidator` - валидация ссылок

**3. Агент экспертизы (Expert Agent)**
- `LegalExpertAgent` - интеллектуальный агент для экспертизы

### Процесс экспертизы (6 этапов)

1. **Поиск документа** на adilet.zan.kz
2. **Получение текста** документа
3. **Проверка консистентности** (структура, ссылки, терминология)
4. **Валидация ссылок** на другие НПА
5. **Поиск связанных документов**
6. **Формирование заключения** с оценкой качества

## ⚙️ Конфигурация

### Основные параметры

```yaml
# config.yaml

agent:
  name: "legal_expert_kz"
  mode: "single"  # single или multi
  max_iterations: 20

tools:
  adilet_search:
    base_url: "https://adilet.zan.kz"
    max_results: 10
    retry_attempts: 3

legal_examination:
  approval_criteria:
    max_critical_issues: 0
    max_warnings: 3
    min_quality_score: 80

security:
  allowed_domains:
    - "adilet.zan.kz"
    - "zan.kz"
  block_external_domains: true
```

### Критерии оценки

Система оценивает документы по 4 критериям:
- **Структура** (30%) - корректность структуры документа
- **Ссылки** (20%) - валидность ссылок на другие НПА
- **Терминология** (20%) - правильность терминов
- **Консистентность** (30%) - общая консистентность

## 📚 API Reference

### AdiletSearchTool

```python
search = AdiletSearchTool()
result = search.execute(
    query="название документа",
    doc_type="law",  # law, code, decree, resolution, order, all
    year="2024",      # опционально
    status="active"   # active, invalid, all
)
```

**Возвращает:**
```python
{
    "status": "success",
    "query": "...",
    "result_count": 10,
    "results": [
        {
            "title": "...",
            "url": "https://adilet.zan.kz/...",
            "number": "...",
            "date": "...",
            "status": "Действует"
        }
    ],
    "source": "adilet.zan.kz"
}
```

### LegalConsistencyChecker

```python
checker = LegalConsistencyChecker()
result = checker.execute(
    document_text="текст документа",
    document_metadata={"title": "...", "number": "...", "date": "..."},
    check_references=True,
    check_structure=True
)
```

**Возвращает:**
```python
{
    "status": "success",
    "overall_assessment": {
        "quality": "Отлично",
        "score": 95,
        "ready_for_approval": True
    },
    "issues": [...],
    "warnings": [...],
    "recommendations": [...]
}
```

### LegalExpertAgent

```python
agent = LegalExpertAgent()
result = agent.execute(
    task="описание задачи"
)
```

**Возвращает:**
```python
{
    "status": "success",
    "task_type": "full_examination",
    "expert_conclusion": {
        "quality_assessment": "...",
        "score": 95,
        "ready_for_approval": True,
        "final_verdict": "..."
    }
}
```

## 🗺️ Дорожная карта

### ✅ Версия 1.0 (текущая)
- Поиск НПА на adilet.zan.kz
- Базовая проверка консистентности
- Выявление противоречий
- Экспертные заключения

### 🔄 Версия 1.1 (в разработке)
- [ ] Улучшенный парсинг HTML adilet.zan.kz
- [ ] Поддержка казахского языка
- [ ] Графы зависимостей между НПА
- [ ] Экспорт результатов в PDF

### 🔮 Версия 2.0 (планируется)
- [ ] Временной анализ изменений НПА
- [ ] Интеграция с ЕСЭДО
- [ ] Автоматическая классификация НПА
- [ ] Уведомления об изменениях
- [ ] Web-интерфейс

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта!

### Как помочь:

1. 🐛 Сообщайте об ошибках (Issues)
2. 💡 Предлагайте новые функции
3. 📝 Улучшайте документацию
4. 🔧 Присылайте Pull Requests

### Процесс разработки:

```bash
# 1. Fork репозитория
# 2. Создайте ветку для новой функции
git checkout -b feature/amazing-feature

# 3. Внесите изменения и закоммитьте
git commit -m "feat: добавлена потрясающая функция"

# 4. Отправьте в свой fork
git push origin feature/amazing-feature

# 5. Создайте Pull Request
```

## 📄 Лицензия

Проект распространяется под лицензией **MIT License**. См. файл [LICENSE](LICENSE) для подробностей.

## 📞 Контакты и поддержка

- 📧 Email: [создайте Issue для вопросов]
- 🐛 Bugs: [GitHub Issues](https://github.com/tymakbayev/LegalTechKZ/issues)
- 💬 Обсуждения: [GitHub Discussions](https://github.com/tymakbayev/LegalTechKZ/discussions)

## 🙏 Благодарности

- Фреймворк [ANUS AI](https://github.com/nikmcfly/ANUS) - основа системы
- [adilet.zan.kz](https://adilet.zan.kz) - официальный источник НПА РК
- Сообщество LegalTech

## ⚠️ Дисклеймер

Данная система предназначена для **предварительного** анализа и **не заменяет** профессиональную правовую экспертизу квалифицированными юристами. Результаты работы системы носят рекомендательный характер.

---

<p align="center">
  Сделано с ❤️ в Казахстане 🇰🇿
</p>

<p align="center">
  <strong>LegalTechKZ</strong> - Будущее правовой экспертизы
</p>
