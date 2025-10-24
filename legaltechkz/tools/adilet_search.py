"""
Инструмент поиска по базе данных НПА РК на adilet.zan.kz

Использует Google Search с оператором site:adilet.zan.kz для более точных результатов.
"""

import logging
import os
import requests
from typing import Dict, Any, Union, List, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, quote
import urllib3

# Отключаем предупреждения о непроверенных HTTPS запросах для adilet.zan.kz
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from legaltechkz.tools.base.tool import BaseTool
from legaltechkz.tools.base.tool_result import ToolResult

logger = logging.getLogger(__name__)


class AdiletSearchTool(BaseTool):
    """
    Инструмент для поиска НПА на adilet.zan.kz

    Позволяет искать:
    - Законы РК
    - Кодексы
    - Указы Президента
    - Постановления Правительства
    - Приказы министерств
    - Другие нормативно-правовые акты
    """

    name = "adilet_search"
    description = "Поиск нормативно-правовых актов РК на adilet.zan.kz"
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Поисковый запрос (название закона, номер, ключевые слова)"
            },
            "doc_type": {
                "type": "string",
                "description": "Тип документа: law (закон), code (кодекс), decree (указ), resolution (постановление), order (приказ)",
                "enum": ["law", "code", "decree", "resolution", "order", "all"]
            },
            "year": {
                "type": "string",
                "description": "Год принятия документа (опционально)"
            },
            "status": {
                "type": "string",
                "description": "Статус документа: active (действующий), invalid (утративший силу)",
                "enum": ["active", "invalid", "all"]
            }
        },
        "required": ["query"]
    }

    # Базовый URL adilet.zan.kz
    BASE_URL = "https://adilet.zan.kz"
    SEARCH_URL = f"{BASE_URL}/rus/search/docs"

    # Типы документов на adilet.zan.kz
    DOC_TYPES = {
        "law": "Закон",
        "code": "Кодекс",
        "decree": "Указ",
        "resolution": "Постановление",
        "order": "Приказ",
        "all": ""
    }

    def __init__(self):
        """Инициализация инструмента поиска Adilet"""
        super().__init__()
        self.session = requests.Session()
        # Улучшенные заголовки для обхода защиты от ботов
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        # Инициализируем сессию, получив главную страницу
        self._init_session()

    def _init_session(self):
        """Инициализировать сессию, посетив главную страницу adilet.zan.kz"""
        try:
            logger.info("Инициализация сессии с adilet.zan.kz")
            # verify=False для обхода проблем с SSL сертификатом adilet.zan.kz
            response = self.session.get(f"{self.BASE_URL}/rus", timeout=10, verify=False)
            if response.status_code == 200:
                logger.info("Сессия успешно инициализирована")
                # Сохраняем cookies для последующих запросов
                return True
            else:
                logger.warning(f"Не удалось инициализировать сессию: {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"Ошибка инициализации сессии: {e}")
            return False

    def execute(
        self,
        query: str,
        doc_type: str = "all",
        year: Optional[str] = None,
        status: str = "active",
        **kwargs
    ) -> Union[Dict[str, Any], ToolResult]:
        """
        Выполнить поиск на adilet.zan.kz

        Args:
            query: Поисковый запрос
            doc_type: Тип документа
            year: Год принятия
            status: Статус документа (действующий/утративший силу)
            **kwargs: Дополнительные параметры

        Returns:
            Результаты поиска с информацией о НПА
        """
        try:
            logger.info(f"Поиск НПА на adilet.zan.kz: '{query}'")

            # Формируем параметры поиска
            search_params = self._build_search_params(query, doc_type, year, status)

            # Выполняем поиск
            results = self._perform_search(search_params)

            if not results:
                logger.warning(f"Документы не найдены по запросу: {query}")

                # Проверяем настроен ли Google Custom Search API
                google_api_key = os.environ.get("GOOGLE_CUSTOM_SEARCH_API_KEY")
                google_cx = os.environ.get("GOOGLE_CUSTOM_SEARCH_CX")

                if not google_api_key or not google_cx:
                    message = (
                        "⚠️ Документы не найдены. Возможная причина: сайт adilet.zan.kz блокирует автоматические запросы.\n\n"
                        "💡 РЕШЕНИЕ: Настройте Google Custom Search API для стабильного поиска:\n"
                        "1. Создайте Custom Search Engine: https://programmablesearchengine.google.com/\n"
                        "2. Получите API ключ: https://console.cloud.google.com/apis/credentials\n"
                        "3. Добавьте в .env файл:\n"
                        "   GOOGLE_CUSTOM_SEARCH_API_KEY=ваш_ключ\n"
                        "   GOOGLE_CUSTOM_SEARCH_CX=ваш_search_engine_id\n\n"
                        "📖 Подробная инструкция: docs/GOOGLE_CUSTOM_SEARCH_SETUP.md\n"
                        "🎁 Бесплатно: 100 запросов в день"
                    )
                else:
                    message = "Документы не найдены. Попробуйте изменить параметры поиска или использовать другие ключевые слова."

                return {
                    "status": "success",
                    "query": query,
                    "results": [],
                    "result_count": 0,
                    "message": message
                }

            logger.info(f"Найдено документов: {len(results)}")

            return {
                "status": "success",
                "query": query,
                "doc_type": doc_type,
                "year": year,
                "status_filter": status,
                "results": results,
                "result_count": len(results),
                "source": "adilet.zan.kz"
            }

        except requests.RequestException as e:
            error_msg = f"Ошибка подключения к adilet.zan.kz: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "suggestion": "Проверьте подключение к интернету и доступность adilet.zan.kz"
            }
        except Exception as e:
            error_msg = f"Ошибка при поиске: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }

    def _build_search_params(
        self,
        query: str,
        doc_type: str,
        year: Optional[str],
        status: str
    ) -> Dict[str, Any]:
        """
        Построить параметры поиска для adilet.zan.kz

        Args:
            query: Поисковый запрос
            doc_type: Тип документа
            year: Год принятия
            status: Статус документа

        Returns:
            Словарь с параметрами поиска
        """
        params = {
            "q": query,
            "lang": "ru"
        }

        # Добавляем тип документа
        if doc_type != "all" and doc_type in self.DOC_TYPES:
            params["type"] = self.DOC_TYPES[doc_type]

        # Добавляем год
        if year:
            params["year"] = year

        # Добавляем статус
        if status == "active":
            params["valid"] = "1"
        elif status == "invalid":
            params["valid"] = "0"

        return params

    def _perform_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Выполнить поиск через Google Custom Search API или напрямую на adilet.zan.kz

        Args:
            params: Параметры поиска

        Returns:
            Список найденных документов
        """
        query = params.get("q", "")
        logger.info(f"Выполняем поиск: '{query}'")

        # Сначала пробуем Google Custom Search API, если есть ключ
        google_api_key = os.environ.get("GOOGLE_CUSTOM_SEARCH_API_KEY")
        google_cx = os.environ.get("GOOGLE_CUSTOM_SEARCH_CX")

        if google_api_key and google_cx:
            logger.info("Используем Google Custom Search API")
            results = self._google_custom_search(query, params, google_api_key, google_cx)
            if results:
                return results
            logger.warning("Google Custom Search API не вернул результатов, используем прямой поиск")

        # Прямой поиск на adilet.zan.kz
        return self._direct_adilet_search(params)

    def _parse_google_results(self, html: str, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Распарсить результаты Google Search

        Args:
            html: HTML страницы результатов Google
            status_filter: Фильтр по статусу (1 - действующий, 0 - утративший силу)

        Returns:
            Список документов
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            results = []

            # Google использует разные классы для результатов
            # Ищем основные блоки результатов
            search_results = soup.find_all('div', class_='g')

            logger.info(f"Найдено блоков результатов Google: {len(search_results)}")

            for result in search_results[:10]:  # Ограничиваем 10 результатами
                try:
                    # Ищем ссылку
                    link_elem = result.find('a', href=True)
                    if not link_elem:
                        continue

                    url = link_elem.get('href', '')

                    # Фильтруем только ссылки на adilet.zan.kz/rus/docs/
                    if 'adilet.zan.kz/rus/docs/' not in url:
                        continue

                    # Извлекаем заголовок
                    title_elem = result.find('h3')
                    title = title_elem.get_text(strip=True) if title_elem else "Без названия"

                    # Извлекаем описание (snippet)
                    snippet_elem = result.find('div', class_=['VwiC3b', 'IsZvec', 'aCOpRe'])
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    # Извлекаем номер и дату из заголовка или snippet
                    doc_number = self._extract_doc_number(title + " " + snippet)
                    doc_date = self._extract_date_from_text(title + " " + snippet)

                    # Определяем статус
                    full_text = (title + " " + snippet).lower()
                    if "утратил" in full_text or "недействующ" in full_text or "признан утратившим" in full_text:
                        status = "Утратил силу"
                    else:
                        status = "Действует"

                    # Применяем фильтр по статусу если указан
                    if status_filter:
                        if status_filter == "1" and status != "Действует":
                            continue
                        elif status_filter == "0" and status != "Утратил силу":
                            continue

                    doc_info = {
                        "title": title,
                        "url": url,
                        "number": doc_number or "Не указан",
                        "date": doc_date or "Не указана",
                        "status": status,
                        "source": "adilet.zan.kz (через Google Search)",
                        "snippet": snippet[:200] if snippet else None
                    }

                    results.append(doc_info)
                    logger.debug(f"Добавлен результат: {title[:50]}...")

                except Exception as e:
                    logger.error(f"Ошибка парсинга результата Google: {e}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Ошибка парсинга результатов Google: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def _google_custom_search(
        self,
        query: str,
        params: Dict[str, Any],
        api_key: str,
        cx: str
    ) -> List[Dict[str, Any]]:
        """
        Выполнить поиск через Google Custom Search JSON API

        Args:
            query: Поисковый запрос
            params: Дополнительные параметры поиска
            api_key: API ключ Google Custom Search
            cx: Custom Search Engine ID

        Returns:
            Список найденных документов
        """
        try:
            # Формируем запрос с site: оператором
            search_query = f"{query} site:adilet.zan.kz"

            # Добавляем фильтры
            doc_type = params.get("type")
            if doc_type:
                search_query += f" {doc_type}"

            year = params.get("year")
            if year:
                search_query += f" {year}"

            # Google Custom Search JSON API endpoint
            api_url = "https://www.googleapis.com/customsearch/v1"
            api_params = {
                "key": api_key,
                "cx": cx,
                "q": search_query,
                "num": 10,  # Максимум 10 результатов
                "lr": "lang_ru",  # Русский язык
            }

            logger.info(f"Google Custom Search запрос: '{search_query}'")

            response = self.session.get(api_url, params=api_params, timeout=15)
            response.raise_for_status()

            data = response.json()
            results = []

            if "items" in data:
                for item in data["items"]:
                    url = item.get("link", "")

                    # Фильтруем только ссылки на документы adilet
                    if "adilet.zan.kz/rus/docs/" not in url:
                        continue

                    title = item.get("title", "Без названия")
                    snippet = item.get("snippet", "")

                    # Извлекаем метаданные
                    doc_number = self._extract_doc_number(title + " " + snippet)
                    doc_date = self._extract_date_from_text(title + " " + snippet)

                    # Определяем статус
                    full_text = (title + " " + snippet).lower()
                    if "утратил" in full_text or "недействующ" in full_text:
                        status = "Утратил силу"
                    else:
                        status = "Действует"

                    # Применяем фильтр по статусу
                    status_filter = params.get("valid")
                    if status_filter:
                        if status_filter == "1" and status != "Действует":
                            continue
                        elif status_filter == "0" and status != "Утратил силу":
                            continue

                    doc_info = {
                        "title": title,
                        "url": url,
                        "number": doc_number or "Не указан",
                        "date": doc_date or "Не указана",
                        "status": status,
                        "source": "adilet.zan.kz (через Google Custom Search API)",
                        "snippet": snippet[:200] if snippet else None
                    }

                    results.append(doc_info)
                    logger.debug(f"Добавлен результат: {title[:50]}...")

                logger.info(f"Найдено через Google Custom Search: {len(results)}")
                return results

            logger.warning("Google Custom Search не вернул результатов")
            return []

        except requests.RequestException as e:
            logger.error(f"Ошибка Google Custom Search API: {e}")
            return []
        except Exception as e:
            logger.error(f"Неожиданная ошибка Google Custom Search: {e}")
            return []

    def _direct_adilet_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Прямой поиск на adilet.zan.kz (запасной вариант)

        Args:
            params: Параметры поиска

        Returns:
            Список документов
        """
        logger.info("Используем прямой поиск на adilet.zan.kz")

        try:
            import time
            # Добавляем небольшую задержку для имитации поведения пользователя
            time.sleep(0.5)

            # Добавляем Referer для более реалистичного запроса
            headers = {
                'Referer': f"{self.BASE_URL}/rus"
            }

            response = self.session.get(
                self.SEARCH_URL,
                params=params,
                headers=headers,
                timeout=15,
                allow_redirects=True,
                verify=False  # Обход проверки SSL для adilet.zan.kz
            )

            logger.info(f"Ответ от adilet.zan.kz: статус {response.status_code}, URL: {response.url}")

            if response.status_code == 403:
                logger.error("Получен 403 Forbidden - сайт блокирует автоматические запросы")
                logger.info("Рекомендация: настройте Google Custom Search API для обхода этой проблемы")
                return []

            response.raise_for_status()
            results = self._parse_search_results(response.text)

            if results:
                logger.info(f"Прямой поиск нашел {len(results)} документов")
            else:
                logger.warning("Прямой поиск не нашел документов")

            return results if results else []

        except requests.HTTPError as e:
            if e.response.status_code == 403:
                logger.error("❌ Сайт adilet.zan.kz блокирует автоматические запросы (403)")
                logger.info("💡 Решение: настройте Google Custom Search API в .env файле")
                logger.info("   GOOGLE_CUSTOM_SEARCH_API_KEY и GOOGLE_CUSTOM_SEARCH_CX")
            else:
                logger.error(f"HTTP ошибка при прямом поиске: {e}")
            return []
        except Exception as e:
            logger.error(f"Ошибка прямого поиска: {e}")
            return []

    def _parse_search_results(self, html: str) -> List[Dict[str, Any]]:
        """
        Распарсить HTML результаты поиска

        Args:
            html: HTML страницы с результатами

        Returns:
            Список документов
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            results = []

            # Ищем различные варианты структуры результатов adilet.zan.kz
            search_items = (
                soup.find_all('div', class_='search-result-item') or
                soup.find_all('div', class_='document-item') or
                soup.find_all('div', class_='doc-item') or
                soup.find_all('tr', class_='document-row') or
                soup.find_all('li', class_='result')
            )

            # Если не нашли специфичные классы, ищем все ссылки на документы
            if not search_items:
                logger.info("Не нашли специфичные элементы, ищем ссылки на документы")
                # Ищем все ссылки которые ведут на /rus/docs/
                links = soup.find_all('a', href=re.compile(r'/rus/docs/[A-Z]'))
                logger.info(f"Найдено ссылок на документы: {len(links)}")

                seen_urls = set()
                for link in links[:20]:  # Проверяем до 20 ссылок
                    doc_info = self._extract_from_link(link)
                    if doc_info and doc_info['url'] not in seen_urls:
                        results.append(doc_info)
                        seen_urls.add(doc_info['url'])
                        if len(results) >= 10:  # Ограничиваем 10 результатами
                            break
            else:
                logger.info(f"Найдено элементов результатов: {len(search_items)}")
                for item in search_items[:10]:  # Ограничиваем 10 результатами
                    doc_info = self._extract_document_info(item)
                    if doc_info:
                        results.append(doc_info)

            logger.info(f"Найдено документов после парсинга: {len(results)}")
            return results

        except Exception as e:
            logger.error(f"Ошибка парсинга результатов: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def _extract_document_info(self, item) -> Optional[Dict[str, Any]]:
        """
        Извлечь информацию о документе из HTML элемента

        Args:
            item: HTML элемент с информацией о документе

        Returns:
            Словарь с информацией о документе
        """
        try:
            # Это упрощенная версия, структура может отличаться
            title_elem = item.find('a', class_='doc-title')
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)
            url = urljoin(self.BASE_URL, title_elem.get('href', ''))

            # Извлекаем номер и дату
            doc_number = self._extract_doc_number(title)
            doc_date = self._extract_doc_date(item)

            # Статус документа
            status_elem = item.find('span', class_='doc-status')
            status = status_elem.get_text(strip=True) if status_elem else "Неизвестно"

            return {
                "title": title,
                "url": url,
                "number": doc_number,
                "date": doc_date,
                "status": status,
                "source": "adilet.zan.kz"
            }

        except Exception as e:
            logger.error(f"Ошибка извлечения информации о документе: {e}")
            return None

    def _extract_doc_number(self, text: str) -> Optional[str]:
        """Извлечь номер документа из текста"""
        # Ищем паттерны типа "№ 123-VI" или "N 123"
        patterns = [
            r'№\s*(\d+(?:-[IVX]+)?)',
            r'N\s*(\d+(?:-[IVX]+)?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return None

    def _extract_doc_date(self, item) -> Optional[str]:
        """Извлечь дату документа"""
        try:
            date_elem = item.find('span', class_='doc-date')
            if date_elem:
                return date_elem.get_text(strip=True)
        except Exception:
            pass

        return None

    def _extract_from_link(self, link) -> Optional[Dict[str, Any]]:
        """
        Извлечь информацию о документе из ссылки

        Args:
            link: BeautifulSoup элемент ссылки

        Returns:
            Словарь с информацией о документе
        """
        try:
            href = link.get('href', '')
            if not href or not href.startswith('/rus/docs/'):
                return None

            url = urljoin(self.BASE_URL, href)
            title = link.get_text(strip=True)

            if not title or len(title) < 10:  # Слишком короткое название - скорее всего не то
                return None

            # Извлекаем номер из title или URL
            doc_number = self._extract_doc_number(title)
            if not doc_number:
                # Попробуем извлечь из URL
                url_match = re.search(r'/docs/([A-Z]\d+)', href)
                if url_match:
                    doc_number = url_match.group(1)

            # Ищем дату в тексте рядом с ссылкой
            parent = link.parent
            date_text = parent.get_text() if parent else title
            doc_date = self._extract_date_from_text(date_text)

            # Определяем статус (по умолчанию - действует если не указано обратное)
            status = "Действует"
            if parent and ("утратил" in parent.get_text().lower() or "недействующ" in parent.get_text().lower()):
                status = "Утратил силу"

            return {
                "title": title,
                "url": url,
                "number": doc_number or "Не указан",
                "date": doc_date or "Не указана",
                "status": status,
                "source": "adilet.zan.kz"
            }

        except Exception as e:
            logger.error(f"Ошибка извлечения из ссылки: {e}")
            return None

    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """Извлечь дату из текста"""
        # Ищем даты в различных форматах
        date_patterns = [
            r'(\d{1,2}\.\d{1,2}\.\d{4})',  # дд.мм.гггг
            r'(\d{1,2}\s+\w+\s+\d{4})',     # дд месяц гггг
            r'от\s+(\d{1,2}\.\d{1,2}\.\d{4})',  # от дд.мм.гггг
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return None

    def _get_demo_results(self, query: str) -> List[Dict[str, Any]]:
        """
        Получить демонстрационные результаты для тестирования

        Args:
            query: Поисковый запрос

        Returns:
            Демо-результаты
        """
        logger.info("Возвращаем демонстрационные результаты для тестирования")

        demo_results = [
            {
                "title": f"Закон Республики Казахстан - результат для '{query}'",
                "url": f"{self.BASE_URL}/rus/docs/example",
                "number": "123-VI",
                "date": "01.01.2024",
                "status": "Действует",
                "source": "adilet.zan.kz (демо)",
                "summary": "Демонстрационный результат. В реальной версии здесь будет актуальная информация с adilet.zan.kz"
            }
        ]

        return demo_results


class AdiletDocumentFetcher(BaseTool):
    """
    Инструмент для получения полного текста документа с adilet.zan.kz
    """

    name = "adilet_fetch_document"
    description = "Получить полный текст НПА с adilet.zan.kz по URL"
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL документа на adilet.zan.kz"
            }
        },
        "required": ["url"]
    }

    def __init__(self):
        """Инициализация инструмента получения документов"""
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def execute(self, url: str, **kwargs) -> Union[Dict[str, Any], ToolResult]:
        """
        Получить полный текст документа

        Args:
            url: URL документа на adilet.zan.kz
            **kwargs: Дополнительные параметры

        Returns:
            Полный текст документа с метаданными
        """
        try:
            # Проверяем, что URL с adilet.zan.kz
            if "adilet.zan.kz" not in url:
                return {
                    "status": "error",
                    "error": "URL должен быть с adilet.zan.kz"
                }

            logger.info(f"Получение документа: {url}")

            # Отправляем запрос
            # verify=False для обхода проблем с SSL сертификатом adilet.zan.kz
            response = self.session.get(url, timeout=15, verify=False)
            response.raise_for_status()

            # Парсим документ
            document = self._parse_document(response.text, url)

            return {
                "status": "success",
                "url": url,
                "document": document,
                "source": "adilet.zan.kz"
            }

        except requests.RequestException as e:
            error_msg = f"Ошибка получения документа: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Ошибка обработки документа: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }

    def _parse_document(self, html: str, url: str) -> Dict[str, Any]:
        """
        Распарсить HTML документа

        Args:
            html: HTML страницы документа
            url: URL документа

        Returns:
            Структурированная информация о документе
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Извлекаем основную информацию
            title = self._extract_title(soup)
            doc_type = self._extract_doc_type(soup)
            number = self._extract_number(soup)
            date = self._extract_date(soup)
            status = self._extract_status(soup)
            text = self._extract_text(soup)

            return {
                "title": title,
                "type": doc_type,
                "number": number,
                "date": date,
                "status": status,
                "text": text,
                "url": url
            }

        except Exception as e:
            logger.error(f"Ошибка парсинга документа: {e}")
            return {
                "title": "Ошибка парсинга",
                "text": "Не удалось извлечь текст документа",
                "error": str(e)
            }

    def _extract_title(self, soup) -> str:
        """Извлечь название документа"""
        title_elem = soup.find('h1') or soup.find('div', class_='doc-title')
        return title_elem.get_text(strip=True) if title_elem else "Без названия"

    def _extract_doc_type(self, soup) -> str:
        """Извлечь тип документа"""
        # Логика извлечения типа документа
        return "Закон"  # Упрощенная версия

    def _extract_number(self, soup) -> Optional[str]:
        """Извлечь номер документа"""
        # Логика извлечения номера
        return None

    def _extract_date(self, soup) -> Optional[str]:
        """Извлечь дату документа"""
        # Логика извлечения даты
        return None

    def _extract_status(self, soup) -> str:
        """Извлечь статус документа"""
        # Логика извлечения статуса
        return "Действует"

    def _extract_text(self, soup) -> str:
        """Извлечь текст документа"""
        # Ищем основной текст документа
        content = soup.find('div', class_='doc-content') or soup.find('div', class_='document-text')

        if content:
            # Очищаем от лишних тегов
            for script in content(['script', 'style']):
                script.decompose()

            return content.get_text(separator='\n', strip=True)

        return "Текст документа не найден"
