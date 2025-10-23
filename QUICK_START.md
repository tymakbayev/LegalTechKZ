# 🚀 Быстрый старт LegalTechKZ

## Шаг 1: Установка зависимостей

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows

# Установить зависимости
pip install -r requirements.txt
pip install -e .
```

## Шаг 2: Настройка API ключей

### Вариант 1: Через .env файл (РЕКОМЕНДУЕТСЯ) ⭐

```bash
# 1. Скопировать пример
cp .env.example .env

# 2. Открыть .env в текстовом редакторе
nano .env   # или любой другой редактор

# 3. Вставить ваши API ключи
```

Пример `.env` файла:
```bash
# Минимум один ключ обязателен
ANTHROPIC_API_KEY=sk-ant-api03-ваш_ключ_здесь

# Опционально (для доступа к другим моделям)
OPENAI_API_KEY=sk-proj-ваш_ключ_здесь
OPENAI_ORG_ID=org-ваша_организация  # Только для корпоративных аккаунтов
GOOGLE_API_KEY=AIzaваш_ключ_здесь
```

**Преимущества .env файла:**
- ✅ Не нужно экспортировать каждый раз
- ✅ Работает автоматически при запуске
- ✅ Безопасно (файл в .gitignore)
- ✅ Легко управлять и редактировать

### Вариант 2: Через export (для одного сеанса)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AI..."
```

**Недостатки:**
- ❌ Нужно экспортировать каждый раз при новом терминале
- ❌ Не сохраняется между сеансами

### Вариант 3: Через ~/.bashrc или ~/.zshrc (постоянно)

Добавьте в конец файла `~/.bashrc` (Linux) или `~/.zshrc` (macOS):

```bash
# LegalTechKZ API Keys
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AI..."
```

Затем:
```bash
source ~/.bashrc  # или source ~/.zshrc
```

## Шаг 3: Запуск

### Web-интерфейс (рекомендуется)

```bash
streamlit run app.py
```

Откроется в браузере: http://localhost:8501

### CLI интерфейс

```bash
python examples/legal_expert_demo.py
```

## 📚 Где получить API ключи?

### Claude (Anthropic) - Рекомендуется для начала
- 🔗 https://console.anthropic.com/
- 💰 $5 бесплатных кредитов при регистрации
- ⭐ Лучше всего для правовой экспертизы

### OpenAI (GPT)
- 🔗 https://platform.openai.com/api-keys
- 💰 $5 бесплатных кредитов (на 3 месяца)

### Google (Gemini)
- 🔗 https://makersuite.google.com/app/apikey
- 💰 Бесплатно до 60 запросов в минуту

### Google Custom Search API (Опционально - для поиска на adilet.zan.kz)
- 🔗 https://programmablesearchengine.google.com/
- 💰 Бесплатно 100 запросов в день
- 📖 Подробная инструкция: [docs/GOOGLE_CUSTOM_SEARCH_SETUP.md](docs/GOOGLE_CUSTOM_SEARCH_SETUP.md)
- ⚠️ **Рекомендуется**: Без этого поиск НПА может не работать из-за защиты adilet.zan.kz от ботов

## ✅ Проверка настройки

После запуска web-интерфейса, посмотрите на **боковую панель слева**:

```
🔑 Статус API ключей
OpenAI GPT-4.1      ✅  (или ❌)
Anthropic Claude    ✅  (или ❌)
Google Gemini       ✅  (или ❌)
```

**Минимум один ключ должен быть ✅ для работы системы!**

## ❓ Проблемы?

### .env файл не работает?

```bash
# Проверьте что python-dotenv установлен
pip install python-dotenv

# Проверьте что файл называется именно .env (без расширения)
ls -la | grep .env

# Файл должен быть в корне проекта (рядом с app.py)
```

### Ключи не распознаются?

```bash
# Проверьте формат в .env (без пробелов, без кавычек)
# Правильно:
ANTHROPIC_API_KEY=sk-ant-123456

# Неправильно:
ANTHROPIC_API_KEY = "sk-ant-123456"  # Лишние пробелы и кавычки
```

### Всё равно не работает?

Попробуйте временно задать через export для проверки:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
streamlit run app.py
```

Если через export работает, значит проблема с .env файлом.

## 📖 Дополнительная документация

- **Подробное руководство по web-интерфейсу:** [docs/WEB_INTERFACE_GUIDE.md](docs/WEB_INTERFACE_GUIDE.md)
- **Настройка API ключей:** [docs/API_KEYS_SETUP.md](docs/API_KEYS_SETUP.md)
- **Система экспертизы:** [docs/LEGAL_EXPERTISE_SYSTEM.md](docs/LEGAL_EXPERTISE_SYSTEM.md)

---

🎉 **Готово! Теперь можете начинать работу с системой!**
