# Настройка Google Custom Search API для поиска на adilet.zan.kz

## Зачем это нужно?

Сайт adilet.zan.kz имеет защиту от автоматических запросов (HTTP 403), поэтому прямой поиск через код может не работать. **Google Custom Search API** решает эту проблему:

- ✅ **Работает стабильно** - обходит защиту от ботов
- ✅ **Бесплатно** - 100 запросов в день бесплатно
- ✅ **Точные результаты** - использует индекс Google
- ✅ **Быстро** - результаты за <1 секунду

## Шаг 1: Создание Custom Search Engine

1. Перейдите на https://programmablesearchengine.google.com/
2. Нажмите **"Добавить"** (Add)
3. Заполните форму:
   - **Название**: "Adilet KZ Search" (или любое другое)
   - **Что искать**: Выберите **"Искать только на этих сайтах"**
   - **Сайты для поиска**: Добавьте `adilet.zan.kz`

   ![Custom Search Engine Setup](https://i.imgur.com/custom-search-example.png)

4. Нажмите **"Создать"**

5. После создания нажмите **"Настроить"** и скопируйте **Search engine ID (cx)**
   - Выглядит примерно так: `a1b2c3d4e5f6g7h8i`
   - Сохраните его - это будет `GOOGLE_CUSTOM_SEARCH_CX`

## Шаг 2: Получение API ключа

1. Перейдите на https://console.cloud.google.com/
2. Создайте новый проект или выберите существующий
3. Перейдите в **APIs & Services → Credentials**
4. Нажмите **"+ CREATE CREDENTIALS" → API key**
5. Скопируйте созданный ключ (выглядит как `AIzaSy...`)
6. (Опционально) Нажмите **"RESTRICT KEY"** и ограничьте использование:
   - **API restrictions**: Выберите **"Custom Search API"**
   - **Application restrictions**: Можно оставить **"None"** или настроить IP restrictions

7. Активируйте Custom Search API:
   - Перейдите в **APIs & Services → Library**
   - Найдите **"Custom Search API"**
   - Нажмите **"Enable"**

## Шаг 3: Добавление ключей в .env файл

Откройте файл `.env` в корне проекта и добавьте:

```bash
# Google Custom Search API для поиска на adilet.zan.kz
GOOGLE_CUSTOM_SEARCH_API_KEY=AIzaSy...  # Ваш API ключ из шага 2
GOOGLE_CUSTOM_SEARCH_CX=a1b2c3d4e5f6g7h8i  # Search engine ID из шага 1
```

**Пример полного .env файла:**

```bash
# LLM API ключи
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...

# Google Custom Search (опционально, но рекомендуется)
GOOGLE_CUSTOM_SEARCH_API_KEY=AIzaSyD...
GOOGLE_CUSTOM_SEARCH_CX=a1b2c3d4e5f6g7h8i
```

## Шаг 4: Проверка работы

Запустите тестовый скрипт:

```bash
python test_google_search.py
```

Если всё настроено правильно, вы увидите:

```
✅ Используем Google Custom Search API
✅ Найдено через Google Custom Search: 5
✅ Поиск через Google Search работает!
```

## Лимиты и цены

### Бесплатный тир
- **100 запросов в день** бесплатно
- Этого достаточно для большинства задач

### Платный тир (если нужно больше)
- $5 за 1000 запросов
- До 10,000 запросов в день

Подробнее: https://developers.google.com/custom-search/v1/overview#pricing

## Альтернатива: Работа без Google Custom Search API

Если вы не хотите настраивать Google API, система будет пытаться использовать прямой поиск на adilet.zan.kz. Однако это может не работать из-за защиты от ботов (HTTP 403).

В этом случае вы увидите сообщение:

```
❌ Сайт adilet.zan.kz блокирует автоматические запросы (403)
💡 Решение: настройте Google Custom Search API в .env файле
```

## Устранение проблем

### Ошибка: "API key not valid"

**Причина**: API ключ неверный или не активирован

**Решение**:
1. Проверьте что ключ скопирован полностью (обычно начинается с `AIza`)
2. Убедитесь что Custom Search API активирован в Google Cloud Console
3. Подождите 1-2 минуты после создания ключа

### Ошибка: "Daily Limit Exceeded"

**Причина**: Превышен лимит 100 запросов в день

**Решение**:
1. Подождите до следующего дня (лимит сбрасывается в полночь UTC)
2. Или включите платный тир в Google Cloud Console

### Ошибка: "Invalid Value for CX"

**Причина**: Search Engine ID неверный

**Решение**:
1. Проверьте что `GOOGLE_CUSTOM_SEARCH_CX` скопирован правильно
2. Зайдите на https://programmablesearchengine.google.com/ и скопируйте ID заново

### Поиск не находит документы

**Возможные причины**:
1. Документ действительно не существует
2. Google ещё не проиндексировал новые документы (обычно задержка 1-2 дня)
3. Слишком специфичный запрос

**Решение**:
- Попробуйте более общий запрос, например:
  - Вместо "Налоговый кодекс РК от 25.12.2017" → "Налоговый кодекс"
  - Вместо "ЗРК №123-VI" → "Закон 123-VI"

## Дополнительная информация

- **Документация Google Custom Search API**: https://developers.google.com/custom-search/v1/overview
- **Programmable Search Engine**: https://programmablesearchengine.google.com/
- **Google Cloud Console**: https://console.cloud.google.com/

## Часто задаваемые вопросы

**Q: Нужен ли мне аккаунт Google Cloud с платёжным методом?**

A: Нет, для бесплатного тира (100 запросов/день) платёжный метод не требуется. Вам нужен только Google аккаунт.

**Q: Можно ли использовать тот же API ключ, что и для Gemini (GOOGLE_API_KEY)?**

A: Нет, это разные ключи. `GOOGLE_API_KEY` для Gemini AI, а `GOOGLE_CUSTOM_SEARCH_API_KEY` для поиска. Вам нужны оба.

**Q: Безопасно ли хранить API ключи в .env файле?**

A: Да, если файл `.env` находится в `.gitignore` и не попадает в репозиторий Git. Проверьте что `.env` указан в `.gitignore`.

**Q: Сколько запросов мне нужно для обычной работы?**

A: Большинству пользователей достаточно бесплатного лимита (100/день). Один поисковый запрос = 1 API запрос.

---

**Готово!** Теперь поиск по adilet.zan.kz будет работать стабильно через Google Custom Search API.
