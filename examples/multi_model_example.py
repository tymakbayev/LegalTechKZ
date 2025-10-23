"""
Пример использования системы автоматического выбора моделей
и pipeline для совместной работы нескольких LLM.

Example of using automatic model selection and pipeline
for collaborative multi-LLM processing.
"""

import os
import sys

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from legaltechkz.models.model_router import ModelRouter
from legaltechkz.models.model_pipeline import create_legal_pipeline, create_qa_pipeline


def example_auto_selection():
    """
    Пример автоматического выбора модели на основе задачи.
    """
    print("=" * 70)
    print("Пример 1: Автоматический выбор модели")
    print("=" * 70)

    # Создаём роутер с включенным автоматическим выбором
    router = ModelRouter(enable_auto_selection=True)

    # Пример 1: Простой вопрос -> GPT-4.1
    simple_query = "Что такое НПА?"
    print(f"\n📝 Запрос: {simple_query}")
    model = router.select_model_for_task(simple_query)
    print(f"✅ Выбрана модель: {model.model_name} ({model.__class__.__name__})")

    # Пример 2: Задача на рассуждение -> Claude Sonnet 4.5
    reasoning_query = "Проанализируй правовые последствия применения статьи 123"
    print(f"\n📝 Запрос: {reasoning_query}")
    model = router.select_model_for_task(reasoning_query)
    print(f"✅ Выбрана модель: {model.model_name} ({model.__class__.__name__})")

    # Пример 3: Большой документ -> Gemini 2.5 Flash
    large_doc_query = "Вот полный текст Гражданского кодекса РК..."
    large_context = "А" * 200000  # Симуляция большого документа
    print(f"\n📝 Запрос: {large_doc_query} (+ {len(large_context)} символов контекста)")
    model = router.select_model_for_task(large_doc_query, context=large_context)
    print(f"✅ Выбрана модель: {model.model_name} ({model.__class__.__name__})")

    print("\n" + "=" * 70)


def example_pipeline_legal_analysis():
    """
    Пример использования pipeline для правовой экспертизы.
    """
    print("=" * 70)
    print("Пример 2: Pipeline для правовой экспертизы")
    print("=" * 70)

    # Создаём pipeline для правовой экспертизы
    pipeline = create_legal_pipeline()

    print("\n📋 Этапы pipeline:")
    for i, stage in enumerate(pipeline.stages, 1):
        print(f"  {i}. {stage.name} ({stage.stage_type})")

    # Симуляция выполнения (без реального вызова API)
    print("\n🔄 Pipeline будет выполнять:")
    print("  1. Gemini обрабатывает большой документ (закон/кодекс)")
    print("  2. Claude проводит глубокий правовой анализ")
    print("  3. GPT-4.1 формирует краткий итоговый ответ")

    # Для реального выполнения:
    # result = pipeline.execute(
    #     initial_input="Полный текст статьи или закона...",
    #     return_all_outputs=True
    # )
    # print(f"\n✅ Результат: {result['final_output']}")

    print("\n" + "=" * 70)


def example_pipeline_qa():
    """
    Пример использования pipeline для вопросов по документу.
    """
    print("=" * 70)
    print("Пример 3: Pipeline для Q&A по документу")
    print("=" * 70)

    # Создаём pipeline для Q&A
    pipeline = create_qa_pipeline()

    print("\n📋 Этапы pipeline:")
    for i, stage in enumerate(pipeline.stages, 1):
        print(f"  {i}. {stage.name} ({stage.stage_type})")

    # Для реального выполнения с вопросом пользователя:
    # question = "Какие штрафы предусмотрены за нарушение?"
    # document = "Полный текст кодекса об административных правонарушениях..."
    #
    # result = pipeline.execute(
    #     initial_input=f"Вопрос: {question}\n\nДокумент: {document}",
    #     template_vars={"question": question, "document": document},
    #     return_all_outputs=True
    # )

    print("\n🔄 Pipeline выполнит:")
    print("  1. Gemini индексирует документ и находит релевантные части")
    print("  2. Claude генерирует детальный ответ с обоснованием")
    print("  3. GPT-4.1 форматирует окончательный ответ")

    print("\n" + "=" * 70)


def example_manual_selection():
    """
    Пример ручного выбора модели.
    """
    print("=" * 70)
    print("Пример 4: Ручной выбор модели")
    print("=" * 70)

    router = ModelRouter(enable_auto_selection=False)

    # Ручное указание провайдера
    configs = [
        {"provider": "openai", "model_name": "gpt-4.1"},
        {"provider": "anthropic", "model_name": "claude-sonnet-4-5"},
        {"provider": "gemini", "model_name": "gemini-2.5-flash"}
    ]

    print("\n📝 Создание моделей:")
    for config in configs:
        model = router.get_model(config)
        print(f"  ✅ {config['provider']}: {model.model_name}")

    print("\n" + "=" * 70)


def example_task_classifier():
    """
    Пример прямого использования TaskClassifier.
    """
    print("=" * 70)
    print("Пример 5: Использование TaskClassifier")
    print("=" * 70)

    from legaltechkz.models.task_classifier import TaskClassifier

    classifier = TaskClassifier()

    test_cases = [
        ("Что такое конституция?", None),
        ("Проанализируй статью 15 УК РК", None),
        ("Вот полный текст закона о банкротстве...", "А" * 300000),
    ]

    print("\n🔍 Классификация задач:")
    for prompt, context in test_cases:
        result = classifier.classify_task(prompt, context)
        print(f"\n  Запрос: {prompt[:50]}...")
        if context:
            print(f"  Контекст: {len(context)} символов")
        print(f"  ✅ Модель: {result['model']}")
        print(f"  📊 Тип: {result['task_type']}")
        print(f"  📝 Причина: {result['reason']}")

    print("\n" + "=" * 70)


def main():
    """
    Запуск всех примеров.
    """
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "СИСТЕМА АВТОМАТИЧЕСКОГО ВЫБОРА МОДЕЛЕЙ" + " " * 19 + "║")
    print("║" + " " * 17 + "LegalTechKZ Multi-Model System" + " " * 21 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    # Проверка API ключей
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Google": os.getenv("GOOGLE_API_KEY")
    }

    print("🔑 Статус API ключей:")
    for name, key in api_keys.items():
        status = "✅ Установлен" if key else "❌ Не установлен"
        print(f"  {name}: {status}")

    if not any(api_keys.values()):
        print("\n⚠️  Предупреждение: Не установлены API ключи.")
        print("   Установите переменные окружения:")
        print("   - OPENAI_API_KEY")
        print("   - ANTHROPIC_API_KEY")
        print("   - GOOGLE_API_KEY")
        print("\n   Примеры будут работать без реальных вызовов API.\n")

    # Запуск примеров
    try:
        example_auto_selection()
        example_pipeline_legal_analysis()
        example_pipeline_qa()
        example_manual_selection()
        example_task_classifier()

        print("\n✅ Все примеры выполнены успешно!\n")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
