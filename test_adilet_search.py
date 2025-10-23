"""
Тестовый скрипт для изучения поиска на adilet.zan.kz

Запуск:
    python test_adilet_search.py
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, parse_qs, urlparse

def test_main_page():
    """Изучить главную страницу и форму поиска"""
    print("=" * 80)
    print("ТЕСТ 1: Изучение главной страницы adilet.zan.kz")
    print("=" * 80)

    try:
        response = requests.get("https://adilet.zan.kz/rus", timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем форму поиска
        search_forms = soup.find_all('form')
        print(f"\n✅ Найдено форм на странице: {len(search_forms)}")

        for i, form in enumerate(search_forms, 1):
            print(f"\n📋 Форма {i}:")
            print(f"   Action: {form.get('action', 'Не указан')}")
            print(f"   Method: {form.get('method', 'GET').upper()}")
            print(f"   ID: {form.get('id', 'Нет')}")
            print(f"   Class: {form.get('class', 'Нет')}")

            # Ищем поля ввода
            inputs = form.find_all(['input', 'select', 'textarea'])
            if inputs:
                print(f"   Поля ({len(inputs)}):")
                for inp in inputs:
                    name = inp.get('name', 'Без имени')
                    inp_type = inp.get('type', inp.name)
                    placeholder = inp.get('placeholder', '')
                    print(f"      - {name} ({inp_type}): {placeholder}")

        # Ищем кнопку "Искать"
        search_buttons = soup.find_all('button', string=re.compile(r'Искать|Поиск', re.I))
        search_buttons += soup.find_all('input', {'type': 'submit', 'value': re.compile(r'Искать|Поиск', re.I)})

        print(f"\n🔍 Найдено кнопок поиска: {len(search_buttons)}")

        # Ищем ссылку на расширенный поиск
        adv_search = soup.find('a', href=re.compile(r'search/advanced|расширенный', re.I))
        if adv_search:
            print(f"\n🔗 Расширенный поиск: {adv_search.get('href')}")

        return True

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False


def test_advanced_search():
    """Изучить страницу расширенного поиска"""
    print("\n" + "=" * 80)
    print("ТЕСТ 2: Изучение расширенного поиска")
    print("=" * 80)

    try:
        response = requests.get("https://adilet.zan.kz/rus/search/advanced", timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем форму
        form = soup.find('form')
        if form:
            print(f"\n📋 Форма расширенного поиска:")
            print(f"   Action: {form.get('action', 'Не указан')}")
            print(f"   Method: {form.get('method', 'GET').upper()}")

            # Все поля
            inputs = form.find_all(['input', 'select', 'textarea'])
            print(f"\n   Поля поиска ({len(inputs)}):")

            for inp in inputs:
                name = inp.get('name', 'Без имени')
                inp_type = inp.get('type', inp.name)
                placeholder = inp.get('placeholder', '')
                value = inp.get('value', '')

                # Для select - показать опции
                if inp.name == 'select':
                    options = inp.find_all('option')
                    opts_text = ', '.join([opt.get_text(strip=True) for opt in options[:5]])
                    print(f"      - {name} (select): {opts_text}...")
                else:
                    print(f"      - {name} ({inp_type}): {placeholder} {value}")

        return True

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False


def test_search_query(query="Налоговый кодекс"):
    """Попробовать выполнить поиск и посмотреть URL"""
    print("\n" + "=" * 80)
    print(f"ТЕСТ 3: Выполнение поиска '{query}'")
    print("=" * 80)

    # Пробуем разные варианты URL
    search_urls = [
        f"https://adilet.zan.kz/rus/search/docs?q={query}",
        f"https://adilet.zan.kz/rus/search?query={query}",
        f"https://adilet.zan.kz/rus/search/docs?text={query}",
        f"https://adilet.zan.kz/rus/search/docs?search={query}",
    ]

    for url in search_urls:
        print(f"\n🔍 Пробуем: {url}")
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)

            print(f"   Статус: {response.status_code}")
            print(f"   Итоговый URL: {response.url}")

            if response.status_code == 200:
                # Проверяем есть ли результаты
                soup = BeautifulSoup(response.text, 'html.parser')

                # Ищем результаты поиска
                results = soup.find_all('a', href=re.compile(r'/rus/docs/[A-Z]'))
                print(f"   Найдено ссылок на документы: {len(results)}")

                if results:
                    print(f"\n   ✅ РАБОТАЕТ! Примеры результатов:")
                    for i, link in enumerate(results[:3], 1):
                        print(f"      {i}. {link.get_text(strip=True)[:70]}...")
                        print(f"         URL: {link.get('href')}")

                    # Анализируем URL результата
                    parsed = urlparse(response.url)
                    params = parse_qs(parsed.query)
                    print(f"\n   📊 Параметры запроса:")
                    for key, value in params.items():
                        print(f"      {key} = {value}")

                    return True

        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

    return False


def analyze_document_urls():
    """Анализировать структуру URL документов"""
    print("\n" + "=" * 80)
    print("ТЕСТ 4: Анализ структуры URL документов")
    print("=" * 80)

    # Примеры известных URL документов
    test_urls = [
        "https://adilet.zan.kz/rus/docs/K1700000120",  # Налоговый кодекс
        "https://adilet.zan.kz/rus/docs/Z1500000401",  # Закон
    ]

    for url in test_urls:
        print(f"\n📄 Анализируем: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                title = soup.find('h1')
                if title:
                    print(f"   Название: {title.get_text(strip=True)[:100]}...")

                # Ищем метаданные
                meta_date = soup.find(string=re.compile(r'\d{2}\.\d{2}\.\d{4}'))
                if meta_date:
                    print(f"   Дата: {meta_date.strip()}")

                # Ищем номер
                doc_number = soup.find(string=re.compile(r'№.*\d+-[IVX]+'))
                if doc_number:
                    print(f"   Номер: {doc_number.strip()}")

        except Exception as e:
            print(f"   ❌ Ошибка: {e}")


def main():
    """Запуск всех тестов"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "АНАЛИЗ ПОИСКА НА ADILET.ZAN.KZ" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    results = {
        "main_page": test_main_page(),
        "advanced_search": test_advanced_search(),
        "search_query": test_search_query("Налоговый кодекс"),
        "document_urls": analyze_document_urls()
    }

    print("\n" + "=" * 80)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 80)

    for test_name, result in results.items():
        status = "✅ Успешно" if result else "❌ Ошибка"
        print(f"{test_name}: {status}")

    print("\n💡 Рекомендации:")
    print("   1. Используйте найденные параметры поиска в AdiletSearchTool")
    print("   2. Обновите _build_search_params() с правильными именами полей")
    print("   3. Настройте SEARCH_URL на основе working URL")
    print("   4. Обновите парсер на основе реальной структуры HTML\n")


if __name__ == "__main__":
    main()
