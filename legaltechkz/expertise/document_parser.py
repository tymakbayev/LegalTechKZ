"""
Document Parser для разбиения НПА на структурные элементы.

Решает проблему пропуска статей при анализе больших документов.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger("legaltechkz.expertise.document_parser")


@dataclass
class DocumentFragment:
    """Фрагмент документа (статья, пункт, подпункт)."""

    type: str  # 'chapter', 'article', 'paragraph', 'subparagraph'
    number: str  # Номер элемента (например, "15", "15.1", "15.1.1")
    title: Optional[str]  # Заголовок (если есть)
    text: str  # Текст фрагмента
    full_path: str  # Полный путь (например, "Глава 3 -> Статья 15 -> Пункт 1")
    parent_number: Optional[str]  # Номер родительского элемента
    char_start: int  # Позиция начала в документе
    char_end: int  # Позиция конца в документе


class NPADocumentParser:
    """
    Парсер НПА документов для структурированного разбиения.

    Создаёт полное оглавление документа для контроля полноты анализа.
    """

    # Паттерны для распознавания структуры НПА
    PATTERNS = {
        'chapter': [
            r'Глава\s+(\d+)\s*\.?\s*([^\n]+)?',
            r'ГЛАВА\s+(\d+)\s*\.?\s*([^\n]+)?',
            r'Раздел\s+(\d+)\s*\.?\s*([^\n]+)?',
        ],
        'article': [
            r'Статья\s+(\d+)\s*\.?\s*([^\n]+)?',
            r'СТАТЬЯ\s+(\d+)\s*\.?\s*([^\n]+)?',
            r'Ст\.\s*(\d+)\s*\.?\s*([^\n]+)?',
        ],
        'paragraph': [
            r'^(\d+)\s*\.\s+([^\n]+)',  # "1. Текст"
            r'^(\d+)\s*\)\s+([^\n]+)',  # "1) Текст"
        ],
        'subparagraph': [
            r'^(\d+)\s*\)\s+([^\n]+)',  # "1) Текст" (внутри пункта)
            r'^\s*([а-я])\s*\)\s+([^\n]+)',  # "а) Текст"
        ]
    }

    def __init__(self):
        """Инициализация парсера."""
        self.fragments: List[DocumentFragment] = []
        self.table_of_contents: Dict[str, DocumentFragment] = {}

    def parse(self, document_text: str) -> List[DocumentFragment]:
        """
        Разбить документ на структурные элементы.

        Args:
            document_text: Полный текст НПА.

        Returns:
            Список фрагментов документа.
        """
        logger.info("Начало парсинга документа")

        self.fragments = []
        self.table_of_contents = {}

        # Разбиваем документ на строки с сохранением позиций
        lines = document_text.split('\n')

        current_chapter = None
        current_article = None
        current_paragraph = None

        char_position = 0

        for line_num, line in enumerate(lines):
            line_stripped = line.strip()

            if not line_stripped:
                char_position += len(line) + 1  # +1 для \n
                continue

            # Проверяем на главу
            chapter_match = self._match_pattern(line_stripped, 'chapter')
            if chapter_match:
                current_chapter = chapter_match['number']
                fragment = DocumentFragment(
                    type='chapter',
                    number=current_chapter,
                    title=chapter_match.get('title'),
                    text=line_stripped,
                    full_path=f"Глава {current_chapter}",
                    parent_number=None,
                    char_start=char_position,
                    char_end=char_position + len(line)
                )
                self.fragments.append(fragment)
                self.table_of_contents[f"chapter_{current_chapter}"] = fragment
                logger.debug(f"Найдена глава: {current_chapter}")

                char_position += len(line) + 1
                continue

            # Проверяем на статью
            article_match = self._match_pattern(line_stripped, 'article')
            if article_match:
                current_article = article_match['number']
                current_paragraph = None  # Сброс при новой статье

                # Собираем полный текст статьи (может быть многострочным)
                article_text = self._collect_article_text(lines, line_num)

                full_path = f"Глава {current_chapter} -> Статья {current_article}" if current_chapter else f"Статья {current_article}"

                fragment = DocumentFragment(
                    type='article',
                    number=current_article,
                    title=article_match.get('title'),
                    text=article_text,
                    full_path=full_path,
                    parent_number=current_chapter,
                    char_start=char_position,
                    char_end=char_position + len(article_text)
                )
                self.fragments.append(fragment)
                self.table_of_contents[f"article_{current_article}"] = fragment
                logger.debug(f"Найдена статья: {current_article}")

                char_position += len(line) + 1
                continue

            # Проверяем на пункт
            paragraph_match = self._match_pattern(line_stripped, 'paragraph')
            if paragraph_match and current_article:
                current_paragraph = paragraph_match['number']

                full_path = f"Статья {current_article} -> Пункт {current_paragraph}"
                if current_chapter:
                    full_path = f"Глава {current_chapter} -> " + full_path

                fragment = DocumentFragment(
                    type='paragraph',
                    number=f"{current_article}.{current_paragraph}",
                    title=None,
                    text=line_stripped,
                    full_path=full_path,
                    parent_number=current_article,
                    char_start=char_position,
                    char_end=char_position + len(line)
                )
                self.fragments.append(fragment)
                self.table_of_contents[f"paragraph_{current_article}_{current_paragraph}"] = fragment
                logger.debug(f"Найден пункт: {current_article}.{current_paragraph}")

            char_position += len(line) + 1

        logger.info(f"Парсинг завершён. Найдено фрагментов: {len(self.fragments)}")
        logger.info(f"Глав: {self._count_by_type('chapter')}, Статей: {self._count_by_type('article')}, Пунктов: {self._count_by_type('paragraph')}")

        return self.fragments

    def _match_pattern(self, text: str, element_type: str) -> Optional[Dict[str, str]]:
        """
        Проверить соответствие текста паттерну.

        Args:
            text: Текст для проверки.
            element_type: Тип элемента (chapter, article, paragraph).

        Returns:
            Словарь с номером и заголовком (если найдено).
        """
        patterns = self.PATTERNS.get(element_type, [])

        for pattern in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                return {
                    'number': groups[0],
                    'title': groups[1].strip() if len(groups) > 1 and groups[1] else None
                }

        return None

    def _collect_article_text(self, lines: List[str], start_line: int) -> str:
        """
        Собрать полный текст статьи (может быть многострочным).

        Args:
            lines: Все строки документа.
            start_line: Номер строки с началом статьи.

        Returns:
            Полный текст статьи.
        """
        article_lines = [lines[start_line].strip()]

        # Собираем следующие строки до новой статьи/пункта
        for i in range(start_line + 1, len(lines)):
            line = lines[i].strip()

            if not line:
                break

            # Если встретили новую статью или пункт - останавливаемся
            if (self._match_pattern(line, 'article') or
                self._match_pattern(line, 'paragraph') or
                self._match_pattern(line, 'chapter')):
                break

            article_lines.append(line)

        return ' '.join(article_lines)

    def _count_by_type(self, element_type: str) -> int:
        """Подсчитать количество элементов определённого типа."""
        return sum(1 for f in self.fragments if f.type == element_type)

    def get_table_of_contents(self) -> List[str]:
        """
        Получить оглавление документа (список всех статей/пунктов).

        Returns:
            Список строк оглавления.
        """
        toc = []

        for fragment in self.fragments:
            if fragment.type == 'article':
                toc.append(f"Статья {fragment.number}: {fragment.title or '(без заголовка)'}")
            elif fragment.type == 'paragraph':
                toc.append(f"  Пункт {fragment.number}")

        return toc

    def get_articles(self) -> List[DocumentFragment]:
        """Получить список всех статей."""
        return [f for f in self.fragments if f.type == 'article']

    def get_article_by_number(self, article_number: str) -> Optional[DocumentFragment]:
        """Получить статью по номеру."""
        return self.table_of_contents.get(f"article_{article_number}")

    def get_fragment_stats(self) -> Dict[str, Any]:
        """
        Получить статистику по фрагментам.

        Returns:
            Словарь со статистикой.
        """
        return {
            'total_fragments': len(self.fragments),
            'chapters': self._count_by_type('chapter'),
            'articles': self._count_by_type('article'),
            'paragraphs': self._count_by_type('paragraph'),
            'subparagraphs': self._count_by_type('subparagraph'),
            'article_numbers': [f.number for f in self.fragments if f.type == 'article']
        }
