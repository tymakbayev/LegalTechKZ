"""
Инструмент для загрузки и парсинга документов с adilet.zan.kz
"""

from typing import Dict, Any
import logging
import requests
from bs4 import BeautifulSoup

from legaltechkz.agents.tools.base_tool import BaseTool
from legaltechkz.expertise.document_parser import DocumentParser

logger = logging.getLogger("legaltechkz.agents.tools.document_fetch")


class DocumentFetchTool(BaseTool):
    """
    Инструмент для загрузки и парсинга документов.

    Используется когда агент нашел документ и хочет:
    - Загрузить полный текст
    - Извлечь конкретную статью
    - Получить структуру документа
    """

    def __init__(self):
        """Инициализация инструмента."""
        self.parser = DocumentParser()
        self.session = requests.Session()
        super().__init__()

    def get_name(self) -> str:
        return "fetch_document"

    def get_description(self) -> str:
        return """Загрузка и парсинг документа с adilet.zan.kz

Используй этот инструмент когда нужно:
- Загрузить полный текст найденного документа
- Извлечь конкретную статью из другого закона
- Получить структуру документа (главы, статьи, пункты)

Параметры:
- url (str): URL документа на adilet.zan.kz
- article_number (int, опционально): Номер статьи для извлечения (если нужна только одна статья)

Возвращает: текст документа или конкретной статьи"""

    def run(self, url: str, article_number: int = None) -> Dict[str, Any]:
        """
        Загрузить и распарсить документ.

        Args:
            url: URL документа
            article_number: Номер статьи (опционально)

        Returns:
            Содержимое документа
        """
        logger.info(f"📄 Загрузка документа: {url}")

        try:
            # Загружаем документ
            response = self.session.get(url, verify=False, timeout=15)
            response.raise_for_status()

            # Парсим HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Извлекаем название
            title_elem = soup.find('h1') or soup.find('title')
            title = title_elem.get_text(strip=True) if title_elem else "Без названия"

            # Извлекаем основной текст
            content_div = soup.find('div', {'class': 'document'}) or soup.find('div', {'id': 'content'})
            if not content_div:
                # Пробуем найти любой контейнер с большим текстом
                content_div = soup.find('body')

            if not content_div:
                raise ValueError("Не удалось найти текст документа")

            full_text = content_div.get_text(separator='\n', strip=True)

            # Парсим структуру
            parsed = self.parser.parse_document(full_text, title)

            # Если запрошена конкретная статья
            if article_number is not None:
                article = self._find_article(parsed['fragments'], article_number)
                if article:
                    logger.info(f"✅ Извлечена статья {article_number}")
                    return {
                        "success": True,
                        "url": url,
                        "title": title,
                        "article_number": article_number,
                        "article_text": article['text'],
                        "article_path": article['full_path'],
                        "message": f"Извлечена {article['full_path']}"
                    }
                else:
                    return {
                        "success": False,
                        "url": url,
                        "message": f"Статья {article_number} не найдена в документе"
                    }

            # Возвращаем весь документ
            logger.info(f"✅ Загружен документ: {parsed['articles_count']} статей")

            return {
                "success": True,
                "url": url,
                "title": title,
                "articles_count": parsed['articles_count'],
                "fragments_count": parsed['fragments_count'],
                "fragments": parsed['fragments'][:10],  # Первые 10 фрагментов
                "table_of_contents": parsed['table_of_contents'][:1000],  # Первые 1000 символов оглавления
                "message": f"Загружен документ '{title}': {parsed['articles_count']} статей"
            }

        except Exception as e:
            logger.error(f"❌ Ошибка загрузки документа: {e}")
            return {
                "success": False,
                "url": url,
                "error": str(e),
                "message": f"Ошибка при загрузке документа: {e}"
            }

    def _find_article(self, fragments, article_number):
        """Найти статью по номеру."""
        for fragment in fragments:
            if fragment.type == 'article' and fragment.number == article_number:
                return {
                    'text': fragment.text,
                    'full_path': fragment.full_path,
                    'number': fragment.number
                }
        return None
