"""
Простой тест ReAct агента без зависимостей
"""

import os
import sys

# Проверка API ключей
if not os.getenv('ANTHROPIC_API_KEY'):
    print("❌ ANTHROPIC_API_KEY не установлен")
    print("Установите его через: export ANTHROPIC_API_KEY=your_key")
    sys.exit(1)

print("✅ API ключи найдены\n")

from legaltechkz.agents.constitutionality_react_agent import ConstitutionalityReActAgent
from legaltechkz.models.anthropic_model import AnthropicModel
from legaltechkz.expertise.document_parser import DocumentFragment

print("="*80)
print("ТЕСТ ReAct АГЕНТА")
print("="*80 + "\n")

# Создаем модель
model = AnthropicModel(model_name="claude-sonnet-4-5", temperature=0.1)
print(f"✅ Модель создана: {model.model_name}\n")

# Создаем ReAct агента
agent = ConstitutionalityReActAgent(model)
print("✅ ReAct агент создан\n")

# Тестовая статья
test_article = DocumentFragment(
    type="article",
    number="15",
    text="""Статья 15. Цифровые права граждан

1. Каждый имеет право на доступ к цифровой информации и услугам.

2. Государство гарантирует защиту персональных данных граждан в цифровой среде в соответствии с Законом Республики Казахстан "О персональных данных и их защите".

3. Ограничение цифровых прав допускается только на основании решения суда в случаях, предусмотренных настоящим Кодексом.

4. Цифровые платформы обязаны обеспечивать хранение персональных данных граждан Казахстана на территории Республики Казахстан.""",
    title="Цифровые права граждан",
    full_path="Глава 2 -> Статья 15",
    parent_number=None,
    char_start=0,
    char_end=500
)

print("📄 АНАЛИЗИРУЕМАЯ СТАТЬЯ:")
print(f"   Номер: {test_article.number}")
print(f"   Название: {test_article.title}")
print(f"   Текст: {test_article.text[:150]}...\n")

print("🚀 Запуск ReAct анализа...\n")
print("="*80 + "\n")

# Запускаем анализ
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
print("ТЕСТ ЗАВЕРШЕН")
print("="*80 + "\n")
