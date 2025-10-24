"""
Тестовый скрипт для проверки реального поиска на adilet.zan.kz
"""

import requests
from bs4 import BeautifulSoup
import urllib3

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_adilet_search():
    """Тестируем реальный поиск на adilet.zan.kz"""

    print("=" * 80)
    print("ТЕСТ: Реальный поиск на adilet.zan.kz")
    print("=" * 80)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    })

    # Сначала инициализируем сессию
    print("\n1. Инициализация сессии...")
    try:
        init_response = session.get("https://adilet.zan.kz/rus", timeout=10, verify=False)
        print(f"   Статус: {init_response.status_code}")
    except Exception as e:
        print(f"   Ошибка: {e}")

    # Теперь пробуем поиск с fulltext параметром
    print("\n2. Поиск с параметром fulltext...")
    search_url = "https://adilet.zan.kz/rus/search/docs"
    params = {
        "fulltext": "Налоговый кодекс"
    }

    try:
        response = session.get(search_url, params=params, timeout=15, verify=False)
        print(f"   Статус: {response.status_code}")
        print(f"   URL: {response.url}")
        print(f"   Длина ответа: {len(response.text)} байт")

        if response.status_code == 200:
            # Сохраняем HTML для анализа
            with open("/tmp/adilet_search_result.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("   ✅ HTML сохранен в /tmp/adilet_search_result.html")

            # Парсим результаты
            soup = BeautifulSoup(response.text, 'html.parser')

            print("\n3. Анализ результатов поиска...")

            # Ищем различные возможные контейнеры результатов
            containers = [
                ('div.search-results', soup.find_all('div', class_='search-results')),
                ('div.result-item', soup.find_all('div', class_='result-item')),
                ('div.document', soup.find_all('div', class_='document')),
                ('tr', soup.find_all('tr')),
                ('li', soup.find_all('li')),
                ('article', soup.find_all('article')),
            ]

            for selector, elements in containers:
                if elements:
                    print(f"\n   Найдено элементов '{selector}': {len(elements)}")

            # Ищем все ссылки на документы
            print("\n4. Поиск ссылок на документы...")
            all_links = soup.find_all('a', href=True)
            doc_links = [link for link in all_links if '/rus/docs/' in link.get('href', '')]

            print(f"   Всего ссылок на документы: {len(doc_links)}")

            if doc_links:
                print("\n   Первые 10 ссылок:")
                for i, link in enumerate(doc_links[:10], 1):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)[:80]
                    print(f"   {i}. {text}")
                    print(f"      URL: {href}")

            # Ищем таблицы
            print("\n5. Поиск таблиц...")
            tables = soup.find_all('table')
            print(f"   Найдено таблиц: {len(tables)}")

            if tables:
                for i, table in enumerate(tables[:3], 1):
                    rows = table.find_all('tr')
                    print(f"   Таблица {i}: {len(rows)} строк")
                    if rows:
                        first_row = rows[0]
                        cells = first_row.find_all(['td', 'th'])
                        print(f"      Первая строка: {len(cells)} ячеек")
                        for j, cell in enumerate(cells[:5], 1):
                            print(f"         Ячейка {j}: {cell.get_text(strip=True)[:50]}")

            # Ищем select/option элементы
            print("\n6. Поиск выпадающих списков...")
            selects = soup.find_all('select')
            print(f"   Найдено select элементов: {len(selects)}")

            for i, select in enumerate(selects, 1):
                select_id = select.get('id', 'no-id')
                select_name = select.get('name', 'no-name')
                options = select.find_all('option')
                print(f"   Select {i} (id={select_id}, name={select_name}): {len(options)} опций")

                if options and i <= 2:  # Показываем опции первых двух select
                    for j, opt in enumerate(options[:10], 1):
                        value = opt.get('value', '')
                        text = opt.get_text(strip=True)
                        print(f"      {j}. value='{value}' text='{text[:60]}'")

        else:
            print(f"   ❌ Ошибка: статус {response.status_code}")

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_adilet_search()
