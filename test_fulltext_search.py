"""
Тестовый скрипт для проверки поиска с параметром fulltext
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from legaltechkz.tools.adilet_search import AdiletSearchTool


def test_fulltext_search():
    """Тестируем поиск с параметром fulltext"""

    print("=" * 80)
    print("ТЕСТ: Поиск на adilet.zan.kz с параметром fulltext")
    print("=" * 80)

    tool = AdiletSearchTool()

    # Тестовые запросы
    test_queries = [
        ("Налоговый кодекс", "code", "active"),
        ("Конституция", "all", "active"),
        ("Трудовой кодекс", "code", "all"),
    ]

    for query, doc_type, status in test_queries:
        print(f"\n{'=' * 80}")
        print(f"Запрос: '{query}'")
        print(f"Тип: {doc_type}, Статус: {status}")
        print(f"{'=' * 80}")

        result = tool.execute(query=query, doc_type=doc_type, status=status)

        print(f"\nСтатус: {result.get('status')}")
        print(f"Найдено: {result.get('result_count', 0)} документов")

        if result.get('status') == 'success' and result.get('results'):
            print(f"\nРезультаты:")
            for i, doc in enumerate(result['results'][:5], 1):
                print(f"\n{i}. {doc.get('title', 'Без названия')[:100]}")
                print(f"   URL: {doc.get('url', 'Нет URL')}")
                print(f"   Номер: {doc.get('number', 'Не указан')}")
                print(f"   Дата: {doc.get('date', 'Не указана')}")
                print(f"   Статус: {doc.get('status', 'Неизвестно')}")
                print(f"   Источник: {doc.get('source', 'Не указан')}")
        elif result.get('message'):
            print(f"\nСообщение:")
            print(result['message'])


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ТЕСТИРОВАНИЕ ПОИСКА С FULLTEXT" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    try:
        test_fulltext_search()

        print("\n" + "=" * 80)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
