#!/usr/bin/env python3
"""
Демонстрационный скрипт системы правовой экспертизы НПА РК

Этот скрипт демонстрирует основные возможности системы:
- Поиск НПА на adilet.zan.kz
- Проверка консистентности документов
- Выявление противоречий
- Полная правовая экспертиза

Использование:
    python examples/legal_expert_demo.py
"""

import sys
import os
import json
from datetime import datetime

# Добавляем путь к модулям anus
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from anus.tools.adilet_search import AdiletSearchTool, AdiletDocumentFetcher
from anus.tools.legal_analysis import (
    LegalConsistencyChecker,
    LegalContradictionDetector,
    LegalReferenceValidator
)
from anus.agents.legal_expert_agent import LegalExpertAgent


def print_header(text):
    """Вывести заголовок"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_section(text):
    """Вывести секцию"""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80 + "\n")


def demo_search():
    """Демонстрация поиска НПА"""
    print_header("ДЕМО 1: Поиск НПА на adilet.zan.kz")

    search_tool = AdiletSearchTool()

    # Пример 1: Поиск кодекса
    print("Поиск: Налоговый кодекс")
    result = search_tool.execute(
        query="Налоговый кодекс",
        doc_type="code",
        status="active"
    )

    print(f"\nНайдено документов: {result['result_count']}")
    print(f"Источник: {result['source']}")

    if result['results']:
        print("\nРезультаты:")
        for i, doc in enumerate(result['results'][:3], 1):
            print(f"\n{i}. {doc['title']}")
            print(f"   Номер: {doc.get('number', 'N/A')}")
            print(f"   Дата: {doc.get('date', 'N/A')}")
            print(f"   Статус: {doc.get('status', 'N/A')}")
            print(f"   URL: {doc['url']}")

    # Пример 2: Поиск закона
    print("\n" + "-" * 40)
    print("Поиск: Закон о государственной службе")
    result2 = search_tool.execute(
        query="государственная служба",
        doc_type="law",
        status="active"
    )

    print(f"\nНайдено документов: {result2['result_count']}")


def demo_consistency_check():
    """Демонстрация проверки консистентности"""
    print_header("ДЕМО 2: Проверка консистентности документа")

    # Демонстрационный текст НПА
    demo_document_text = """
    ЗАКОН РЕСПУБЛИКИ КАЗАХСТАН

    О внесении изменений в некоторые законодательные акты

    Статья 1. Общие положения

    Настоящий Закон регулирует отношения в сфере государственного управления.

    Под государственным управлением понимается деятельность государственных органов.

    Статья 2. Основные понятия

    В настоящем Законе используются следующие основные понятия:

    1) государственный орган - это орган исполнительной власти;
    2) должностное лицо - лицо, занимающее государственную должность.

    Статья 3. Ссылки на другие НПА

    В соответствии с Конституцией Республики Казахстан и Законом Республики Казахстан
    от 23 ноября 2015 года № 416-V "О государственной службе" устанавливаются следующие нормы.

    Статья 5. Заключительные положения

    Настоящий Закон вводится в действие со дня его официального опубликования.
    """

    checker = LegalConsistencyChecker()

    print("Выполняю проверку консистентности документа...")

    result = checker.execute(
        document_text=demo_document_text,
        document_metadata={
            "title": "Закон РК о внесении изменений",
            "number": "123-VI",
            "date": "01.01.2024"
        },
        check_references=True,
        check_structure=True
    )

    # Выводим результаты
    print_section("Результаты проверки")

    # Общая оценка
    assessment = result.get('overall_assessment', {})
    print(f"Качество документа: {assessment.get('quality', 'N/A')}")
    print(f"Оценка: {assessment.get('score', 0)}/100")
    print(f"Готов к принятию: {'Да' if assessment.get('ready_for_approval') else 'Нет'}")

    # Структура
    structure = result.get('checks', {}).get('structure', {}).get('structure', {})
    print(f"\nСтруктурный анализ:")
    print(f"  Обнаружено статей: {len(structure.get('articles', []))}")
    print(f"  Обнаружено глав: {len(structure.get('chapters', []))}")

    # Ссылки
    references = result.get('checks', {}).get('references', {})
    print(f"\nАнализ ссылок:")
    print(f"  Найдено ссылок на НПА: {references.get('total_references', 0)}")

    # Проблемы
    issues = result.get('issues', [])
    if issues:
        print(f"\nКритические замечания ({len(issues)}):")
        for issue in issues:
            print(f"  - [{issue.get('severity', 'medium')}] {issue.get('message')}")
    else:
        print("\nКритических замечаний не обнаружено.")

    # Предупреждения
    warnings = result.get('warnings', [])
    if warnings:
        print(f"\nПредупреждения ({len(warnings)}):")
        for warning in warnings[:5]:  # Показываем первые 5
            print(f"  - {warning.get('message')}")
    else:
        print("\nПредупреждений нет.")

    # Рекомендации
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"\nРекомендации:")
        for rec in recommendations:
            print(f"  - {rec}")


def demo_contradiction_detection():
    """Демонстрация выявления противоречий"""
    print_header("ДЕМО 3: Выявление противоречий между документами")

    # Демонстрационные документы
    doc1 = {
        "title": "Закон о защите прав потребителей",
        "number": "234-V",
        "date": "12.03.2010",
        "text": """
        Статья 5. Основные понятия

        Под потребителем понимается физическое лицо, приобретающее товары или услуги
        для личного, семейного или домашнего использования.

        Гарантийный срок составляет 12 месяцев с момента передачи товара.
        """
    }

    doc2 = {
        "title": "Гражданский кодекс РК",
        "number": "188-V",
        "date": "27.12.1994",
        "text": """
        Статья 10. Определения

        Потребитель - это гражданин, использующий, приобретающий товар (работу, услугу)
        для бытовых нужд, не связанных с извлечением прибыли.

        Гарантийный срок устанавливается продавцом и составляет не менее 6 месяцев.
        """
    }

    detector = LegalContradictionDetector()

    print("Сравниваю документы...")
    print(f"\nДокумент 1: {doc1['title']}")
    print(f"Документ 2: {doc2['title']}")

    result = detector.execute(
        document1=doc1,
        document2=doc2,
        scope="definitions"
    )

    print_section("Результаты сравнения")

    print(f"Обнаружено противоречий: {result['contradictions_count']}")
    print(f"Есть конфликты: {'Да' if result['has_conflicts'] else 'Нет'}")

    if result['contradictions']:
        print("\nПротиворечия:")
        for i, contra in enumerate(result['contradictions'], 1):
            print(f"\n{i}. Тип: {contra.get('type')}")
            print(f"   Термин: {contra.get('term')}")
            print(f"   Определение в док. 1: {contra.get('definition1', 'N/A')[:100]}...")
            print(f"   Определение в док. 2: {contra.get('definition2', 'N/A')[:100]}...")
            print(f"   Критичность: {contra.get('severity')}")


def demo_full_examination():
    """Демонстрация полной правовой экспертизы"""
    print_header("ДЕМО 4: Полная правовая экспертиза")

    agent = LegalExpertAgent(name="demo_legal_expert")

    print("Запуск полной правовой экспертизы...")
    print("(В демо-режиме используются демонстрационные данные)\n")

    # Выполняем экспертизу
    result = agent.execute(
        task="Провести полную правовую экспертизу Налогового кодекса РК"
    )

    # Проверяем успешность
    if result.get('status') == 'error':
        print(f"Ошибка: {result.get('error')}")
        print("\nПримечание: Это демо-версия. Для реальной работы требуется:")
        print("- Доступ к adilet.zan.kz")
        print("- API ключ для LLM модели")
        return

    print_section("Этапы экспертизы")

    stages = result.get('stages', {})
    for stage_name, stage_data in stages.items():
        status = stage_data.get('status', 'unknown')
        status_emoji = "✓" if status == "completed" else "⊘" if status == "skipped" else "○"
        print(f"{status_emoji} {stage_name.replace('_', ' ').title()}: {status}")

    # Экспертное заключение
    conclusion = result.get('expert_conclusion', {})

    if conclusion:
        print_section("Экспертное заключение")

        doc_info = conclusion.get('document', {})
        print(f"Документ: {doc_info.get('title', 'N/A')}")
        print(f"Номер: {doc_info.get('number', 'N/A')}")
        print(f"Дата: {doc_info.get('date', 'N/A')}")
        print(f"Дата экспертизы: {conclusion.get('examination_date', 'N/A')}")

        print(f"\nОценка качества: {conclusion.get('quality_assessment', 'N/A')}")
        print(f"Балл: {conclusion.get('score', 0)}/100")
        print(f"Готов к принятию: {'Да' if conclusion.get('ready_for_approval') else 'Нет'}")

        # Критические замечания
        critical = conclusion.get('critical_issues', [])
        if critical:
            print(f"\nКритические замечания ({len(critical)}):")
            for issue in critical[:3]:
                print(f"  - [{issue.get('severity', 'N/A')}] {issue.get('description')}")

        # Рекомендации
        recommendations = conclusion.get('recommendations', [])
        if recommendations:
            print(f"\nРекомендации ({len(recommendations)}):")
            for rec in recommendations[:3]:
                print(f"  - {rec}")

        print(f"\nИтоговое заключение:")
        print(f"  {conclusion.get('final_verdict', 'N/A')}")


def demo_reference_validation():
    """Демонстрация валидации ссылок"""
    print_header("ДЕМО 5: Валидация ссылок на НПА")

    validator = LegalReferenceValidator()

    # Демонстрационные ссылки
    demo_references = [
        "Закон Республики Казахстан от 23 ноября 2015 года № 416-V 'О государственной службе'",
        "Налоговый кодекс Республики Казахстан",
        "Указ Президента РК от 01.01.2020 № 100",
        "Постановление Правительства",  # Неполная ссылка
        "Закон № 123",  # Неполная ссылка
    ]

    print("Проверяю ссылки на НПА...\n")

    result = validator.execute(
        references=demo_references,
        check_online=False  # Отключаем онлайн проверку для демо
    )

    print(f"Всего ссылок: {result['total_references']}")
    print(f"Валидных: {result['valid_references']}")
    print(f"Невалидных: {result['invalid_references']}")

    print("\nДетальные результаты:")
    for i, ref_result in enumerate(result['results'], 1):
        status = "✓ Валидна" if ref_result['is_valid'] else "✗ Невалидна"
        print(f"\n{i}. {status}")
        print(f"   Ссылка: {ref_result['reference']}")
        if ref_result['issues']:
            print(f"   Проблемы: {', '.join(ref_result['issues'])}")


def main():
    """Главная функция"""
    print("\n" + "=" * 80)
    print("  ДЕМОНСТРАЦИЯ СИСТЕМЫ ПРАВОВОЙ ЭКСПЕРТИЗЫ НПА РК")
    print("  Версия: 1.0")
    print("  Дата: " + datetime.now().strftime("%d.%m.%Y %H:%M"))
    print("=" * 80)

    print("\nВнимание: Это демонстрационная версия с тестовыми данными.")
    print("Для работы с реальными данными требуется:")
    print("  - Подключение к adilet.zan.kz")
    print("  - API ключ для LLM модели (OpenAI/Anthropic)")
    print("\nНажмите Enter для продолжения...")
    input()

    try:
        # Демо 1: Поиск
        demo_search()
        input("\nНажмите Enter для следующей демонстрации...")

        # Демо 2: Проверка консистентности
        demo_consistency_check()
        input("\nНажмите Enter для следующей демонстрации...")

        # Демо 3: Выявление противоречий
        demo_contradiction_detection()
        input("\nНажмите Enter для следующей демонстрации...")

        # Демо 4: Валидация ссылок
        demo_reference_validation()
        input("\nНажмите Enter для следующей демонстрации...")

        # Демо 5: Полная экспертиза
        demo_full_examination()

        print_header("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("Спасибо за внимание!")
        print("\nДля получения дополнительной информации см. файл LEGAL_EXPERT_README.md")

    except KeyboardInterrupt:
        print("\n\nДемонстрация прервана пользователем.")
    except Exception as e:
        print(f"\n\nОшибка: {str(e)}")
        print("Это демо-версия. Некоторые функции могут быть недоступны.")


if __name__ == "__main__":
    main()
