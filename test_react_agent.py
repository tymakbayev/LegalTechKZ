"""
Тестовый скрипт для демонстрации ReAct агента

Показывает как агент:
1. Анализирует статью
2. Извлекает ссылки
3. Ищет Конституцию
4. Загружает документы
5. Формирует обоснованное заключение
"""

import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/react_agent_test.log', encoding='utf-8')
    ]
)

from legaltechkz.agents.constitutionality_react_agent import ConstitutionalityReActAgent
from legaltechkz.models.model_router import ModelRouter
from legaltechkz.expertise.document_parser import DocumentFragment


def test_react_agent():
    """Тестирование ReAct агента на примере статьи."""

    print("\n" + "="*80)
    print("ДЕМОНСТРАЦИЯ ReAct АГЕНТА")
    print("="*80 + "\n")

    # Создаем модель
    model_router = ModelRouter(enable_auto_selection=True)
    model = model_router.select_model_for_pipeline_stage("analysis")

    print(f"✅ Используем модель: {model.model_name}\n")

    # Создаем ReAct агента
    agent = ConstitutionalityReActAgent(model)

    # Тестовая статья (пример)
    test_article = DocumentFragment(
        type="article",
        number=15,
        text="""Статья 15. Цифровые права граждан

1. Каждый имеет право на доступ к цифровой информации и услугам.

2. Государство гарантирует защиту персональных данных граждан в цифровой среде в соответствии с Законом Республики Казахстан "О персональных данных и их защите".

3. Ограничение цифровых прав допускается только на основании решения суда в случаях, предусмотренных настоящим Кодексом.

4. Цифровые платформы обязаны обеспечивать хранение персональных данных граждан Казахстана на территории Республики Казахстан.""",
        title="Цифровые права граждан",
        level=0,
        parent_chapter=None,
        parent_paragraph=None
    )

    print("📄 АНАЛИЗИРУЕМАЯ СТАТЬЯ:")
    print(f"   Номер: {test_article.number}")
    print(f"   Название: {test_article.title}")
    print(f"   Текст: {test_article.text[:200]}...\n")

    # Запускаем анализ
    print("🚀 Запуск ReAct анализа...\n")
    print("="*80 + "\n")

    result = agent.analyze_article(test_article)

    # Выводим результаты
    print("\n" + "="*80)
    print("РЕЗУЛЬТАТ АНАЛИЗА")
    print("="*80 + "\n")

    if result["success"]:
        print(f"✅ Статус: УСПЕШНО")
        print(f"🔄 Итераций: {result['iterations']}")
        print(f"\n📋 АНАЛИЗ:\n")
        print(result["analysis"])

        print(f"\n\n🧠 ПРОЦЕСС МЫШЛЕНИЯ АГЕНТА:\n")
        print(result["thinking_process"])

    else:
        print(f"❌ Статус: ОШИБКА")
        print(f"Ошибка: {result.get('error')}")

    print("\n" + "="*80)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_react_agent()
