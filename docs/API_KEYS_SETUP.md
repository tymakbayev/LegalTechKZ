# Настройка API ключей

Подробная инструкция по настройке API ключей для работы с LegalTechKZ.

## Обзор

Система LegalTechKZ использует три LLM провайдера:
- **OpenAI** (GPT-4.1) - для быстрых ответов и суммаризации
- **Anthropic** (Claude Sonnet 4.5) - для глубокого анализа
- **Google** (Gemini 2.5 Flash) - для обработки больших документов

## Настройка переменных окружения

### 1. OpenAI

OpenAI требует API ключ и **опционально** organization ID (если вы работаете в рамках организации).

#### Только API ключ (для личных аккаунтов):

```bash
export OPENAI_API_KEY="sk-..."
```

#### API ключ + Organization ID (для корпоративных аккаунтов):

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_ORG_ID="org-..."
```

**Как получить:**
1. Перейдите на https://platform.openai.com/api-keys
2. Создайте новый API ключ
3. Если у вас корпоративный аккаунт:
   - Перейдите в Settings → Organization
   - Скопируйте Organization ID (начинается с `org-`)

### 2. Anthropic (Claude)

Anthropic требует только API ключ:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Как получить:**
1. Перейдите на https://console.anthropic.com/
2. Перейдите в API Keys
3. Создайте новый API ключ

### 3. Google (Gemini)

Google требует только API ключ:

```bash
export GOOGLE_API_KEY="AI..."
```

**Как получить:**
1. Перейдите на https://aistudio.google.com/app/apikey
2. Создайте новый API ключ
3. Или используйте Google Cloud Console для создания API ключа

## Способы настройки

### Вариант 1: Через командную строку (временно)

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_ORG_ID="org-..."  # Опционально
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AI..."
```

**Важно:** Эти переменные будут доступны только в текущей сессии терминала.

### Вариант 2: Через .bashrc / .zshrc (постоянно)

Добавьте в файл `~/.bashrc` (или `~/.zshrc` для zsh):

```bash
# LegalTechKZ API Keys
export OPENAI_API_KEY="sk-..."
export OPENAI_ORG_ID="org-..."  # Опционально
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AI..."
```

Затем перезагрузите конфигурацию:

```bash
source ~/.bashrc  # или source ~/.zshrc
```

### Вариант 3: Через .env файл

Создайте файл `.env` в корне проекта:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...  # Опционально

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-...

# Google Configuration
GOOGLE_API_KEY=AI...
```

Затем загрузите переменные с помощью python-dotenv:

```python
from dotenv import load_dotenv
load_dotenv()

# Теперь можно использовать систему
from legaltechkz.expertise.legal_expertise_pipeline import LegalExpertisePipeline
```

**Установка python-dotenv:**

```bash
pip install python-dotenv
```

### Вариант 4: Программная настройка

Вы можете передать ключи напрямую при создании моделей:

```python
from legaltechkz.models.openai_model import OpenAIModel
from legaltechkz.models.anthropic_model import AnthropicModel
from legaltechkz.models.gemini_model import GeminiModel

# OpenAI с organization
openai_model = OpenAIModel(
    model_name="gpt-4.1",
    api_key="sk-...",
    organization="org-..."  # Опционально
)

# Anthropic
anthropic_model = AnthropicModel(
    model_name="claude-sonnet-4-5",
    api_key="sk-ant-..."
)

# Google Gemini
gemini_model = GeminiModel(
    model_name="gemini-2.5-flash",
    api_key="AI..."
)
```

## Проверка настройки

Запустите скрипт проверки:

```python
import os

api_keys = {
    "OpenAI API Key": os.getenv("OPENAI_API_KEY"),
    "OpenAI Org ID": os.getenv("OPENAI_ORG_ID"),
    "Anthropic API Key": os.getenv("ANTHROPIC_API_KEY"),
    "Google API Key": os.getenv("GOOGLE_API_KEY")
}

print("Статус API ключей:")
for name, key in api_keys.items():
    if key:
        # Показываем только начало ключа для безопасности
        masked_key = key[:10] + "..." if len(key) > 10 else "***"
        print(f"✅ {name}: {masked_key}")
    else:
        status = "⚠️  (опционально)" if "Org ID" in name else "❌ НЕ УСТАНОВЛЕН"
        print(f"{status} {name}")
```

## Важные замечания

### OpenAI Organization ID

**Когда нужен Organization ID:**
- ✅ У вас корпоративный аккаунт OpenAI
- ✅ Вы работаете в рамках организации
- ✅ У вас есть несколько проектов в организации

**Когда НЕ нужен Organization ID:**
- ❌ У вас личный аккаунт OpenAI
- ❌ Вы используете бесплатный tier

### Проверка через API

```python
# Проверка OpenAI
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")  # Опционально
)

try:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": "Тест"}],
        max_tokens=10
    )
    print("✅ OpenAI работает")
except Exception as e:
    print(f"❌ Ошибка OpenAI: {e}")

# Проверка Anthropic
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

try:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": "Тест"}],
        max_tokens=10
    )
    print("✅ Anthropic работает")
except Exception as e:
    print(f"❌ Ошибка Anthropic: {e}")

# Проверка Google
from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Тест"
    )
    print("✅ Google работает")
except Exception as e:
    print(f"❌ Ошибка Google: {e}")
```

## Безопасность

⚠️ **НИКОГДА не коммитьте API ключи в git!**

Добавьте в `.gitignore`:

```
.env
*.key
api_keys.txt
```

## Стоимость использования

Примерная стоимость на март 2025:

| Провайдер | Модель | Вход (за 1M токенов) | Выход (за 1M токенов) |
|-----------|--------|----------------------|------------------------|
| OpenAI | GPT-4.1 | $10 | $30 |
| Anthropic | Claude Sonnet 4.5 | $3 | $15 |
| Google | Gemini 2.5 Flash | Бесплатно (60 req/min) | Бесплатно |

**Совет:** Начните с Gemini для тестирования (бесплатно), затем добавьте платные модели.

## Поддержка

Если у вас проблемы с настройкой:

1. Проверьте что переменные окружения установлены: `echo $OPENAI_API_KEY`
2. Проверьте формат ключей (OpenAI начинается с `sk-`, Anthropic с `sk-ant-`, Google с `AI`)
3. Проверьте квоты на платформах провайдеров
4. Для OpenAI: если у вас organization, обязательно укажите `OPENAI_ORG_ID`

## Быстрый старт

```bash
# 1. Установите ключи
export OPENAI_API_KEY="sk-..."
export OPENAI_ORG_ID="org-..."  # Если есть
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AI..."

# 2. Запустите пример
python examples/multi_model_example.py

# 3. Запустите правовую экспертизу
python examples/legal_expertise_example.py
```
