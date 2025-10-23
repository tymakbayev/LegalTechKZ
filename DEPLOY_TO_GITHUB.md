# Инструкция по переносу кода в ваш репозиторий LegalTechKZ

## Способ 1: Через командную строку (рекомендуется)

### Шаг 1: Клонируйте ваш репозиторий

```bash
cd ~/projects  # или любая другая директория
git clone https://github.com/tymakbayev/LegalTechKZ.git
cd LegalTechKZ
```

### Шаг 2: Скопируйте файлы из подготовленной директории

Если вы работаете в том же окружении, где был создан код:

```bash
# Копируем все файлы
cp -r /home/user/npa-legal-expert/* .
cp /home/user/npa-legal-expert/.gitignore .

# Проверяем
ls -la
```

### Шаг 3: Закоммитьте и отправьте в GitHub

```bash
git add .
git commit -m "feat: Система правовой экспертизы НПА РК

Реализована AI-powered система для правовой экспертизы нормативно-правовых
актов Республики Казахстан.

Основные возможности:
- Поиск НПА на adilet.zan.kz
- Проверка консистентности документов
- Выявление противоречий между НПА
- Валидация ссылок
- Формирование экспертных заключений

Компоненты:
- anus/tools/adilet_search.py - поиск на adilet.zan.kz
- anus/tools/legal_analysis.py - инструменты анализа
- anus/agents/legal_expert_agent.py - агент экспертизы
- config.yaml - конфигурация системы
- examples/legal_expert_demo.py - демонстрация

Документация:
- README.md - полное руководство
- QUICKSTART_LEGAL.md - быстрый старт
- ADAPTATION_SUMMARY.md - техническое резюме"

git push origin main
```

### Шаг 4: Создайте тэг версии (опционально)

```bash
git tag -a v1.0.0 -m "Release v1.0.0: Initial release of Legal Expert System"
git push origin v1.0.0
```

---

## Способ 2: Через GitHub веб-интерфейс

### Если репозиторий пустой:

1. Перейдите в ваш репозиторий: https://github.com/tymakbayev/LegalTechKZ

2. Нажмите "Add file" → "Upload files"

3. Загрузите все файлы из директории `/home/user/npa-legal-expert/`:
   - Всю папку `anus/`
   - Папку `examples/`
   - Папку `data/`
   - Файлы: README.md, config.yaml, requirements.txt, setup.py, .gitignore, etc.

4. Добавьте commit message и нажмите "Commit changes"

---

## Способ 3: Через архив (если работаете на другой машине)

### На машине, где был создан код:

```bash
# Архив уже создан в /home/user/LegalTechKZ.tar.gz
# Скопируйте его на вашу локальную машину
```

### На вашей локальной машине:

```bash
# Распакуйте архив
tar -xzf LegalTechKZ.tar.gz
cd npa-legal-expert

# Клонируйте ваш репозиторий
cd ..
git clone https://github.com/tymakbayev/LegalTechKZ.git
cd LegalTechKZ

# Скопируйте файлы
cp -r ../npa-legal-expert/* .
cp ../npa-legal-expert/.gitignore .

# Коммит и push
git add .
git commit -m "feat: Initial release - Legal Expert System for Kazakhstan NPA"
git push origin main
```

---

## Список файлов для переноса

Убедитесь, что следующие файлы и папки присутствуют:

### Основные файлы:
- [x] README.md (полная документация)
- [x] QUICKSTART_LEGAL.md (быстрый старт)
- [x] ADAPTATION_SUMMARY.md (резюме адаптации)
- [x] config.yaml (конфигурация)
- [x] requirements.txt (зависимости)
- [x] setup.py (установка пакета)
- [x] LICENSE (лицензия MIT)
- [x] .gitignore

### Код системы (папка anus/):
- [x] anus/tools/adilet_search.py (поиск на adilet.zan.kz)
- [x] anus/tools/legal_analysis.py (анализ НПА)
- [x] anus/agents/legal_expert_agent.py (агент экспертизы)
- [x] anus/core/ (ядро системы)
- [x] anus/models/ (LLM модели)
- [x] anus/ui/ (интерфейс)

### Примеры:
- [x] examples/legal_expert_demo.py (интерактивное демо)
- [x] examples/README.md

### Директории:
- [x] data/ (для кэша и памяти)
- [x] logs/ (для логов)
- [x] results/ (для результатов)

---

## После переноса

### 1. Настройка на новой машине:

```bash
# Клонируйте ваш репозиторий
git clone https://github.com/tymakbayev/LegalTechKZ.git
cd LegalTechKZ

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt
pip install -e .

# Настройте API ключ
export OPENAI_API_KEY="ваш_ключ_здесь"

# Запустите демо
python examples/legal_expert_demo.py
```

### 2. Создайте красивый README на GitHub:

В корне репозитория уже есть README.md с:
- Описанием проекта
- Инструкциями по установке
- Примерами использования
- API Reference
- Документацией

### 3. Добавьте темы (Topics) в GitHub:

Перейдите в Settings → и добавьте темы:
- `legal-tech`
- `kazakhstan`
- `ai`
- `nlp`
- `legal-analysis`
- `adilet`
- `law`
- `python`

### 4. Создайте Release:

1. Перейдите в "Releases" → "Create a new release"
2. Tag: v1.0.0
3. Title: "Initial Release: Legal Expert System for Kazakhstan NPA"
4. Описание: см. в ADAPTATION_SUMMARY.md

---

## Проверка работоспособности

После переноса проверьте:

```bash
# Тест импорта
python -c "from anus.tools.adilet_search import AdiletSearchTool; print('OK')"

# Запуск демо
python examples/legal_expert_demo.py

# Простой тест
python -c "
from anus.tools.adilet_search import AdiletSearchTool
search = AdiletSearchTool()
result = search.execute(query='Налоговый кодекс', doc_type='code')
print(f'Найдено: {result[\"result_count\"]} документов')
"
```

---

## Поддержка

Если возникнут вопросы:
1. Проверьте QUICKSTART_LEGAL.md
2. Смотрите примеры в examples/
3. Читайте полную документацию в README.md

Удачи с вашим проектом LegalTechKZ! 🇰🇿
