"""
Настройка централизованного логирования для LegalTechKZ.

Все логи сохраняются в папку logs/ в корне проекта.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[str] = None,
    session_name: Optional[str] = None
) -> logging.Logger:
    """
    Настроить логирование для всего приложения.

    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        log_dir: Директория для логов (по умолчанию: ./logs)
        session_name: Имя сессии для файла логов

    Returns:
        Корневой logger
    """
    # Определяем директорию проекта
    project_root = Path(__file__).parent.parent.parent

    # Создаем папку logs в корне проекта
    if log_dir is None:
        log_dir = project_root / "logs"
    else:
        log_dir = Path(log_dir)

    log_dir.mkdir(exist_ok=True)

    # Имя файла лога с timestamp
    if session_name is None:
        session_name = f"expertise_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    log_file = log_dir / f"{session_name}.log"

    # Настройка форматирования
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Корневой logger
    root_logger = logging.getLogger("legaltechkz")
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Очищаем предыдущие handlers
    root_logger.handlers.clear()

    # Handler для файла
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # В файл пишем всё
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Handler для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    root_logger.info("=" * 80)
    root_logger.info(f"Логирование инициализировано: {log_file}")
    root_logger.info(f"Уровень логирования: {log_level}")
    root_logger.info("=" * 80)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Получить logger для модуля.

    Args:
        name: Имя модуля (обычно __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"legaltechkz.{name}")


def create_session_log_dir(session_id: str) -> Path:
    """
    Создать отдельную папку для логов сессии.

    Args:
        session_id: ID сессии

    Returns:
        Path к директории логов сессии
    """
    project_root = Path(__file__).parent.parent.parent
    session_dir = project_root / "logs" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    return session_dir
