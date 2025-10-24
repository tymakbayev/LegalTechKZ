"""
Проверка что все импорты работают корректно
"""

print("Проверка импортов ReAct агентов...\n")

try:
    print("1. Импорт базовых инструментов...")
    from legaltechkz.agents.tools import BaseTool, AdiletSearchTool, DocumentFetchTool, ReferenceExtractorTool
    print("   ✅ Инструменты импортированы")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
    exit(1)

try:
    print("2. Импорт ReAct агента...")
    from legaltechkz.agents.react_agent import ReActAgent
    print("   ✅ ReAct агент импортирован")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
    exit(1)

try:
    print("3. Импорт ConstitutionalityReActAgent...")
    from legaltechkz.agents.constitutionality_react_agent import ConstitutionalityReActAgent
    print("   ✅ ConstitutionalityReActAgent импортирован")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
    exit(1)

try:
    print("4. Импорт web_integration...")
    from legaltechkz.ui.web_integration import get_controller
    print("   ✅ web_integration импортирован")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
    exit(1)

try:
    print("5. Проверка создания инструментов...")
    search_tool = AdiletSearchTool()
    print(f"   ✅ AdiletSearchTool: {search_tool.name}")

    fetch_tool = DocumentFetchTool()
    print(f"   ✅ DocumentFetchTool: {fetch_tool.name}")

    ref_tool = ReferenceExtractorTool()
    print(f"   ✅ ReferenceExtractorTool: {ref_tool.name}")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
    exit(1)

print("\n" + "="*80)
print("✅ ВСЕ ИМПОРТЫ РАБОТАЮТ КОРРЕКТНО!")
print("="*80)
print("\nReAct агенты готовы к использованию!")
print("\nДля полного теста запустите:")
print("  streamlit run app.py")
print("\nИли (если есть API ключи):")
print("  python test_react_agent.py")
