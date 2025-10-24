"""
Компонент для отображения live-логов экспертизы в стиле "Thinking..."

Показывает пользователю что именно происходит внутри каждого этапа.
"""

import streamlit as st
import time
import os
from pathlib import Path
from typing import Optional


def display_live_logs(log_file_path: str, interval: float = 0.5, max_lines: int = 50):
    """
    Отображает live-логи из файла с автообновлением.

    Args:
        log_file_path: Путь к файлу логов
        interval: Интервал обновления в секундах
        max_lines: Максимальное количество строк для показа
    """
    log_container = st.empty()
    last_size = 0

    while True:
        if os.path.exists(log_file_path):
            current_size = os.path.getsize(log_file_path)

            if current_size > last_size:
                # Читаем новые строки
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    f.seek(last_size)
                    new_content = f.read()

                    # Обновляем контейнер
                    log_container.code(new_content, language='log')

                last_size = current_size

        time.sleep(interval)


def create_thinking_expander(stage_name: str, log_content: str = "") -> None:
    """
    Создает expander в стиле "Thinking..." для этапа экспертизы.

    Args:
        stage_name: Название этапа
        log_content: Содержимое логов для отображения
    """
    with st.expander(f"🧠 {stage_name} - детали обработки", expanded=False):
        if log_content:
            # Парсим логи и форматируем красиво
            log_lines = log_content.split('\n')

            for line in log_lines[-50:]:  # Последние 50 строк
                if '[INFO]' in line:
                    st.markdown(f"ℹ️ {line.split('[INFO]')[1].strip()}")
                elif '[WARNING]' in line:
                    st.warning(line.split('[WARNING]')[1].strip())
                elif '[ERROR]' in line:
                    st.error(line.split('[ERROR]')[1].strip())
                elif '[DEBUG]' in line:
                    st.text(f"🔍 {line.split('[DEBUG]')[1].strip()}")
                elif 'Группа' in line:
                    st.info(line.strip())
                elif '✅' in line or '🔄' in line:
                    st.success(line.strip())
        else:
            st.info("Логи появятся здесь во время обработки...")


def extract_stage_logs(full_log_path: str, stage_name: str) -> str:
    """
    Извлекает логи конкретного этапа из общего файла логов.

    Args:
        full_log_path: Путь к полному файлу логов
        stage_name: Название этапа для фильтрации

    Returns:
        Логи этапа
    """
    if not os.path.exists(full_log_path):
        return ""

    stage_logs = []
    capture = False

    with open(full_log_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Начало этапа
            if stage_name in line and 'Начало' in line:
                capture = True

            # Собираем строки этапа
            if capture:
                stage_logs.append(line.rstrip())

            # Конец этапа
            if stage_name in line and 'завершён' in line:
                capture = False
                break

    return '\n'.join(stage_logs)


def create_progress_summary(
    stage_name: str,
    total_articles: int,
    processed_articles: int = 0,
    current_action: str = ""
) -> None:
    """
    Создает краткую сводку прогресса для этапа.

    Args:
        stage_name: Название этапа
        total_articles: Всего статей
        processed_articles: Обработано статей
        current_action: Текущее действие
    """
    progress_value = processed_articles / total_articles if total_articles > 0 else 0

    with st.container():
        st.progress(progress_value, text=f"{stage_name}: {processed_articles}/{total_articles} статей")

        if current_action:
            st.caption(f"🔄 {current_action}")


# Пример использования для интеграции в app.py:
"""
from legaltechkz.ui.thinking_display import create_thinking_expander, extract_stage_logs

# После завершения этапа:
if results.get("log_file"):
    stage_log_content = extract_stage_logs(results["log_file"], stage_name)
    create_thinking_expander(stage_name, stage_log_content)
"""
