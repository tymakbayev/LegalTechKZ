"""
Тестовый скрипт для проверки Google Search интеграции

Запуск:
    python test_google_search.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from legaltechkz.tools.adilet_search import AdiletSearchTool


def test_google_search():
    """Протестировать поиск через Google"""
    print("=" * 80)
    print("ТЕСТ: Поиск через Google с site:adilet.zan.kz")
    print("=" * 80)

    tool = AdiletSearchTool()

    # Тестовый запрос
    query = "Налоговый кодекс"

    print(f"\n🔍 Выполняем поиск: '{query}'")
    print("-" * 80)

    result = tool.execute(query=query, doc_type="code", status="active")

    print(f"\n📊 Результат:")
    print(f"   Статус: {result.get('status')}")
    print(f"   Найдено документов: {result.get('result_count', 0)}")

    if result.get('status') == 'success' and result.get('results'):
        print(f"\n📄 Документы:\n")
        for i, doc in enumerate(result['results'][:5], 1):  # Первые 5
            print(f"   {i}. {doc.get('title', 'Без названия')[:80]}")
            print(f"      URL: {doc.get('url', 'Нет URL')}")
            print(f"      Номер: {doc.get('number', 'Не указан')}")
            print(f"      Дата: {doc.get('date', 'Не указана')}")
            print(f"      Статус: {doc.get('status', 'Неизвестно')}")
            print(f"      Источник: {doc.get('source', 'Не указан')}")
            print()
    else:
        error = result.get('error', result.get('message', 'Неизвестная ошибка'))
        print(f"\n   ❌ Ошибка: {error}")

    # Проверяем что результаты из Google
    if result.get('results'):
        first_result = result['results'][0]
        if 'Google Search' in first_result.get('source', ''):
            print("✅ Поиск через Google Search работает!")
        else:
            print("⚠️ Результаты не из Google Search")

    return result


def test_different_queries():
    """Тестировать разные типы запросов"""
    print("\n" + "=" * 80)
    print("ТЕСТ: Различные запросы")
    print("=" * 80)

    tool = AdiletSearchTool()

    queries = [
        ("Конституция Республики Казахстан", "code", "active"),
        ("Трудовой кодекс", "code", "active"),
        ("Закон о языках", "law", "all"),
    ]

    for query, doc_type, status in queries:
        print(f"\n🔍 Запрос: '{query}' (тип: {doc_type}, статус: {status})")
        result = tool.execute(query=query, doc_type=doc_type, status=status)
        count = result.get('result_count', 0)
        print(f"   Результатов: {count}")

        if count > 0:
            first = result['results'][0]
            print(f"   Первый: {first.get('title', '')[:60]}...")
            print(f"   Источник: {first.get('source', '')}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 18 + "ТЕСТИРОВАНИЕ GOOGLE SEARCH ИНТЕГРАЦИИ" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    try:
        # Основной тест
        result = test_google_search()

        # Дополнительные тесты
        test_different_queries()

        print("\n" + "=" * 80)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 80)

        if result.get('status') == 'success':
            print("\n✅ Google Search интеграция работает корректно!")
        else:
            print("\n⚠️ Возможны проблемы с подключением к Google или парсингом")
            print("   Попробуйте запустить позже или проверьте интернет-подключение")

    except Exception as e:
        print(f"\n❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
