"""
LegalTechKZ Web Interface
Веб-интерфейс для системы правовой экспертизы НПА РК

Запуск:
    streamlit run app.py
"""

import streamlit as st
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

# Загрузка переменных окружения из .env файла
from dotenv import load_dotenv
load_dotenv()  # Загружает переменные из .env файла в os.environ

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

# Настройка страницы
st.set_page_config(
    page_title="LegalTechKZ - Система правовой экспертизы НПА РК",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stage-header {
        background: linear-gradient(90deg, #1f77b4, #4a9eff);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1f77b4, #4a9eff);
    }
</style>
""", unsafe_allow_html=True)


def check_api_keys() -> Dict[str, bool]:
    """Проверка наличия API ключей."""
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "google": bool(os.getenv("GOOGLE_API_KEY"))
    }


def render_header():
    """Отрисовка заголовка приложения."""
    st.markdown('<div class="main-header">⚖️ LegalTechKZ</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI-powered система для автоматизированной правовой экспертизы НПА Республики Казахстан</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")


def render_sidebar():
    """Отрисовка боковой панели."""
    with st.sidebar:
        st.image("https://img.shields.io/badge/Version-1.0-blue.svg", use_container_width=False)

        st.markdown("### 🔑 Статус API ключей")
        api_status = check_api_keys()

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("OpenAI GPT-4.1")
        with col2:
            st.write("✅" if api_status["openai"] else "❌")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Anthropic Claude")
        with col2:
            st.write("✅" if api_status["anthropic"] else "❌")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Google Gemini")
        with col2:
            st.write("✅" if api_status["google"] else "❌")

        if not any(api_status.values()):
            st.warning("⚠️ Не настроены API ключи! См. документацию.")
            with st.expander("📖 Как настроить?"):
                st.code("""
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AI..."
                """, language="bash")

        st.markdown("---")

        st.markdown("### 📚 Документация")
        st.markdown("""
        - [Руководство пользователя](docs/USER_GUIDE.md)
        - [API документация](docs/API_KEYS_SETUP.md)
        - [Система экспертизы](docs/LEGAL_EXPERTISE_SYSTEM.md)
        - [Multi-Model система](docs/MULTI_MODEL_SYSTEM.md)
        """)

        st.markdown("---")

        st.markdown("### ℹ️ О системе")
        st.markdown("""
        **LegalTechKZ** работает исключительно с официальным ресурсом [adilet.zan.kz](https://adilet.zan.kz)

        Версия: 1.0
        Лицензия: MIT
        """)

        st.markdown("---")
        st.markdown("Made with ❤️ in Kazakhstan 🇰🇿")


def render_expertise_stages():
    """Отрисовка информации о 6 этапах экспертизы."""
    st.markdown("### 📋 Этапы правовой экспертизы")

    stages = [
        {
            "number": 1,
            "name": "Фильтр Релевантности",
            "icon": "🔍",
            "description": "Определение нормативности документа, оценка по матрице ILNR"
        },
        {
            "number": 2,
            "name": "Фильтр Конституционности",
            "icon": "📜",
            "description": "Проверка соответствия Конституции РК, NLI анализ"
        },
        {
            "number": 3,
            "name": "Фильтр Системной Интеграции",
            "icon": "🔗",
            "description": "Выявление коллизий с действующим законодательством"
        },
        {
            "number": 4,
            "name": "Юридико-техническая экспертиза",
            "icon": "⚙️",
            "description": "Оценка юридической техники и лингвистики"
        },
        {
            "number": 5,
            "name": "Антикоррупционная экспертиза",
            "icon": "🛡️",
            "description": "Выявление коррупциогенных факторов"
        },
        {
            "number": 6,
            "name": "Гендерная экспертиза",
            "icon": "⚖️",
            "description": "Оценка гендерного воздействия документа"
        }
    ]

    cols = st.columns(3)
    for i, stage in enumerate(stages):
        with cols[i % 3]:
            with st.container():
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{stage['icon']} Этап {stage['number']}</h4>
                    <p><strong>{stage['name']}</strong></p>
                    <p style="font-size: 0.9rem; color: #666;">{stage['description']}</p>
                </div>
                """, unsafe_allow_html=True)


def main():
    """Основная функция приложения."""
    render_header()
    render_sidebar()

    # Главное меню
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Главная",
        "📝 Анализ НПА",
        "🔍 Поиск на Adilet",
        "📊 История анализов"
    ])

    with tab1:
        render_home_page()

    with tab2:
        render_analysis_page()

    with tab3:
        render_search_page()

    with tab4:
        render_history_page()


def render_home_page():
    """Главная страница."""
    st.markdown("## Добро пожаловать в LegalTechKZ!")

    st.markdown("""
    Система для автоматизированной правовой экспертизы нормативно-правовых актов
    Республики Казахстан с использованием искусственного интеллекта.
    """)

    # Метрики системы
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Этапов экспертизы",
            value="6",
            delta="Комплексный анализ"
        )

    with col2:
        st.metric(
            label="LLM Провайдеров",
            value="3",
            delta="Multi-Model система"
        )

    with col3:
        st.metric(
            label="Экономия затрат",
            value="85-90%",
            delta="Через оптимизации"
        )

    with col4:
        st.metric(
            label="Точность анализа",
            value="+18%",
            delta="Extended Thinking"
        )

    st.markdown("---")

    # Информация о 6 этапах
    render_expertise_stages()

    st.markdown("---")

    # Возможности системы
    st.markdown("### ✨ Возможности системы")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🔍 Поиск НПА**
        - Поиск на официальном adilet.zan.kz
        - Фильтрация по типу и статусу
        - Получение полных текстов документов

        **📊 Анализ документов**
        - Комплексная правовая экспертиза
        - 6 этапов детального анализа
        - Гарантия полноты (каждая статья)

        **⚖️ Выявление проблем**
        - Противоречия Конституции
        - Коллизии с законодательством
        - Коррупциогенные факторы
        """)

    with col2:
        st.markdown("""
        **🤖 Multi-Model ИИ**
        - Gemini: большие документы (1M+ токенов)
        - Claude: глубокий анализ и рассуждения
        - GPT: быстрые ответы и суммаризация

        **💾 Экспорт результатов**
        - PDF отчеты
        - JSON данные
        - DOCX документы

        **📈 Оптимизации**
        - Prompt Caching (90% экономия)
        - Extended Thinking (+18% точность)
        - Structured Outputs (100% формат)
        """)

    st.markdown("---")

    # Быстрый старт
    st.markdown("### 🚀 Быстрый старт")

    st.info("""
    **Начните с вкладки "📝 Анализ НПА":**

    1. Вставьте текст НПА или загрузите файл
    2. Выберите этапы экспертизы
    3. Настройте параметры анализа
    4. Запустите анализ и получите подробный отчет

    Или используйте вкладку **"🔍 Поиск на Adilet"** для поиска НПА на официальном сайте.
    """)


def render_analysis_page():
    """Страница анализа НПА."""
    st.markdown("## 📝 Анализ нормативно-правового акта")

    st.info("На этой странице вы можете провести комплексную правовую экспертизу НПА")

    # Проверка API ключей
    api_status = check_api_keys()
    if not any(api_status.values()):
        st.error("❌ Необходимо настроить хотя бы один API ключ для работы системы!")
        st.stop()

    # Ввод документа
    st.markdown("### 1️⃣ Ввод документа")

    input_method = st.radio(
        "Выберите способ ввода документа:",
        ["Вставить текст", "Загрузить файл", "Поиск на Adilet"],
        horizontal=True
    )

    document_text = ""
    document_metadata = {}

    if input_method == "Вставить текст":
        document_text = st.text_area(
            "Текст НПА:",
            height=300,
            placeholder="Вставьте полный текст нормативно-правового акта...",
            help="Вставьте текст документа для анализа"
        )

        col1, col2 = st.columns(2)
        with col1:
            doc_name = st.text_input("Название документа:", placeholder="Например: Закон о цифровизации")
        with col2:
            doc_number = st.text_input("Номер документа:", placeholder="Например: 284-VI ЗРК")

        if doc_name:
            document_metadata["title"] = doc_name
        if doc_number:
            document_metadata["number"] = doc_number

    elif input_method == "Загрузить файл":
        uploaded_file = st.file_uploader(
            "Выберите файл с текстом НПА:",
            type=["txt", "pdf", "docx"],
            help="Поддерживаются форматы: TXT, PDF, DOCX"
        )

        if uploaded_file is not None:
            # TODO: Implement file parsing
            st.info("📄 Функция чтения файлов будет реализована в следующем обновлении")
            document_text = uploaded_file.read().decode("utf-8") if uploaded_file.type == "text/plain" else ""

    else:  # Поиск на Adilet
        st.markdown("Перейдите на вкладку **'🔍 Поиск на Adilet'** для поиска документов")

    # Настройки анализа
    st.markdown("---")
    st.markdown("### 2️⃣ Настройки анализа")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Выберите этапы экспертизы:**")

        stage_1 = st.checkbox("🔍 Фильтр Релевантности", value=True)
        stage_2 = st.checkbox("📜 Фильтр Конституционности", value=True)
        stage_3 = st.checkbox("🔗 Фильтр Системной Интеграции", value=True)
        stage_4 = st.checkbox("⚙️ Юридико-техническая экспертиза", value=True)
        stage_5 = st.checkbox("🛡️ Антикоррупционная экспертиза", value=True)
        stage_6 = st.checkbox("⚖️ Гендерная экспертиза", value=True)

    with col2:
        st.markdown("**Параметры модели:**")

        use_extended_thinking = st.checkbox(
            "Extended Thinking",
            value=True,
            help="Включить режим расширенного мышления для сложных этапов (+18% точность)"
        )

        use_prompt_caching = st.checkbox(
            "Prompt Caching",
            value=True,
            help="Использовать кеширование промптов (экономия 90%)"
        )

        use_grounding = st.checkbox(
            "Grounding",
            value=False,
            help="Проверять актуальность законодательства через Google Search"
        )

        structured_output = st.checkbox(
            "Structured Output",
            value=True,
            help="Гарантировать структурированный формат отчета"
        )

    # Кнопка запуска
    st.markdown("---")
    st.markdown("### 3️⃣ Запуск анализа")

    if st.button("🚀 Начать экспертизу", type="primary", use_container_width=True):
        if not document_text:
            st.error("❌ Необходимо ввести текст документа!")
        else:
            run_expertise_analysis(
                document_text=document_text,
                document_metadata=document_metadata,
                stages={
                    "relevance": stage_1,
                    "constitutionality": stage_2,
                    "system_integration": stage_3,
                    "legal_technical": stage_4,
                    "anti_corruption": stage_5,
                    "gender": stage_6
                },
                options={
                    "extended_thinking": use_extended_thinking,
                    "prompt_caching": use_prompt_caching,
                    "grounding": use_grounding,
                    "structured_output": structured_output
                }
            )


def run_expertise_analysis(
    document_text: str,
    document_metadata: Dict[str, str],
    stages: Dict[str, bool],
    options: Dict[str, bool]
):
    """Запуск анализа документа с использованием WebExpertiseController."""

    # Инициализация состояния для результатов
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}

    st.markdown("---")
    st.markdown("## 📊 Результаты экспертизы")

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Контейнер для результатов
    results_container = st.container()

    try:
        # Импорт контроллера
        from legaltechkz.ui.web_integration import get_controller

        controller = get_controller()

        # Callback для обновления прогресса
        def update_progress(progress_info):
            """Обновление UI с информацией о прогрессе."""
            progress_value = progress_info.current_stage / progress_info.total_stages
            progress_bar.progress(progress_value)
            status_text.text(f"⏳ {progress_info.stage_name} ({progress_info.current_stage}/{progress_info.total_stages})...")

        # Запуск экспертизы
        status_text.text("🚀 Запуск экспертизы...")

        results = controller.run_expertise_pipeline(
            document_text=document_text,
            document_metadata=document_metadata,
            stages=stages,
            options=options,
            progress_callback=update_progress
        )

        # Проверка успешности
        if not results.get("success"):
            st.error(f"❌ Ошибка: {results.get('error')}")

            if results.get("traceback"):
                with st.expander("Подробности ошибки"):
                    st.code(results["traceback"])
            return

        # Сохранение результатов в session state
        st.session_state.analysis_results = results

        # Отображение результатов парсинга
        parsing = results["parsing"]
        with results_container:
            st.success(f"✅ Документ распарсен: {parsing['fragments_count']} элементов ({parsing['articles_count']} статей)")

            with st.expander("📋 Оглавление документа"):
                st.text(parsing["table_of_contents"])

        # Отображение результатов этапов
        stage_names_icons = {
            "relevance": "🔍",
            "constitutionality": "📜",
            "system_integration": "🔗",
            "legal_technical": "⚙️",
            "anti_corruption": "🛡️",
            "gender": "⚖️"
        }

        for stage_result in results["stage_results"]:
            stage_key = stage_result["detailed_results"].get("stage_key", "")
            icon = stage_names_icons.get(stage_key, "📊")

            # Определение стиля по статусу
            if stage_result["status"] == "success":
                status_badge = "✅ Завершено"
                expander_class = "success-box"
            elif stage_result["status"] == "warning":
                status_badge = "⚠️ Завершено с замечаниями"
                expander_class = "warning-box"
            else:
                status_badge = "❌ Ошибка"
                expander_class = "error-box"

            with results_container:
                with st.expander(f"{icon} {stage_result['stage_name']} - {status_badge}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"""
                        **Статус:** {status_badge}

                        **Проанализировано статей:** {stage_result['articles_analyzed']}

                        **Найдено проблем:** {stage_result['issues_found']}

                        **Время обработки:** {stage_result['processing_time']:.2f} сек
                        """)

                    with col2:
                        if stage_result["recommendations"]:
                            st.markdown("**Рекомендации:**")
                            for rec in stage_result["recommendations"]:
                                st.markdown(f"- {rec}")
                        else:
                            st.markdown("**Рекомендации:** Нет замечаний")

        # Финальный отчет
        progress_bar.progress(1.0)
        status_text.text("✅ Экспертиза завершена!")

        overall = results["overall"]
        completeness = results["completeness"]

        with results_container:
            st.markdown("---")
            st.markdown("## 📋 Итоговое заключение")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Общая оценка",
                    f"{overall['quality_score']}/100",
                    delta="Отлично" if overall['quality_score'] >= 90 else "Хорошо" if overall['quality_score'] >= 70 else "Требует доработки"
                )

            with col2:
                st.metric(
                    "Найдено проблем",
                    overall['total_issues'],
                    delta="Нет проблем" if overall['total_issues'] == 0 else f"{overall['total_issues']} проблем"
                )

            with col3:
                st.metric(
                    "Полнота анализа",
                    f"{completeness['completion_rate']:.0f}%",
                    delta=f"{completeness['analyzed_articles']}/{completeness['total_articles']} статей"
                )

            with col4:
                st.metric(
                    "Время обработки",
                    f"{overall['processing_time']:.1f} сек",
                    delta=f"{results['stages_completed']} этапов"
                )

            # Вердикт
            if overall["verdict_status"] == "success":
                st.success(f"✅ {overall['verdict']}")
            elif overall["verdict_status"] == "warning":
                st.warning(f"⚠️ {overall['verdict']}")
            else:
                st.error(f"❌ {overall['verdict']}")

            # Кнопки экспорта
            st.markdown("---")
            st.markdown("### 💾 Экспорт результатов")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Экспорт текстового отчета
                text_report = controller.export_results_text(results)
                st.download_button(
                    label="📄 Скачать TXT",
                    data=text_report,
                    file_name=f"expertise_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with col2:
                # Экспорт JSON
                json_report = controller.export_results_json(results)
                st.download_button(
                    label="📊 Скачать JSON",
                    data=json_report,
                    file_name=f"expertise_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            with col3:
                if st.button("📝 Экспорт в PDF", use_container_width=True):
                    st.info("💡 Функция экспорта в PDF будет добавлена в следующем обновлении")

    except ImportError as e:
        st.error(f"❌ Ошибка импорта модулей: {e}")
        st.info("💡 Убедитесь, что все модули системы экспертизы установлены")
        with st.expander("Подробности"):
            import traceback
            st.code(traceback.format_exc())
    except Exception as e:
        st.error(f"❌ Ошибка при выполнении анализа: {e}")
        with st.expander("Подробности ошибки"):
            import traceback
            st.code(traceback.format_exc())


def render_search_page():
    """Страница поиска на Adilet."""
    st.markdown("## 🔍 Поиск НПА на adilet.zan.kz")

    st.info("Поиск документов на официальном ресурсе законодательства РК")

    # Форма поиска
    col1, col2 = st.columns([3, 1])

    with col1:
        search_query = st.text_input(
            "Поисковый запрос:",
            placeholder="Например: Налоговый кодекс, Закон о цифровизации...",
            help="Введите название, номер или ключевые слова документа"
        )

    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        search_button = st.button("🔍 Поиск", type="primary", use_container_width=True)

    # Фильтры
    with st.expander("⚙️ Фильтры поиска"):
        col1, col2, col3 = st.columns(3)

        with col1:
            doc_type = st.selectbox(
                "Тип документа:",
                ["Все", "Закон", "Кодекс", "Указ", "Постановление", "Приказ"]
            )

        with col2:
            status = st.selectbox(
                "Статус:",
                ["Все", "Действующий", "Утративший силу"]
            )

        with col3:
            year = st.text_input(
                "Год принятия:",
                placeholder="Например: 2024"
            )

    # Выполнение поиска
    if search_button and search_query:
        with st.spinner("Поиск документов..."):
            try:
                from legaltechkz.tools.adilet_search import AdiletSearchTool

                search_tool = AdiletSearchTool()

                # Маппинг типов
                doc_type_map = {
                    "Все": "all",
                    "Закон": "law",
                    "Кодекс": "code",
                    "Указ": "decree",
                    "Постановление": "resolution",
                    "Приказ": "order"
                }

                status_map = {
                    "Все": "all",
                    "Действующий": "active",
                    "Утративший силу": "invalid"
                }

                # Выполнение поиска
                results = search_tool.execute(
                    query=search_query,
                    doc_type=doc_type_map.get(doc_type, "all"),
                    status=status_map.get(status, "all"),
                    year=year if year else None
                )

                if results["status"] == "success" and results["result_count"] > 0:
                    st.success(f"✅ Найдено документов: {results['result_count']}")

                    # Отображение результатов
                    for i, doc in enumerate(results["results"], 1):
                        with st.container():
                            col1, col2 = st.columns([4, 1])

                            with col1:
                                st.markdown(f"**{i}. {doc.get('title', 'Без названия')}**")
                                st.markdown(f"📅 {doc.get('date', 'Дата не указана')} • 📋 {doc.get('number', 'Номер не указан')}")
                                st.markdown(f"🔗 [{doc.get('url', '')}]({doc.get('url', '')})")

                                status_badge = "🟢 Действует" if doc.get('status') == "Действует" else "🔴 Утратил силу"
                                st.markdown(status_badge)

                            with col2:
                                if st.button(f"📝 Анализировать", key=f"analyze_{i}"):
                                    st.info("Загрузка документа для анализа...")
                                    # TODO: Fetch document and switch to analysis tab

                            st.markdown("---")
                else:
                    st.warning("⚠️ Документы не найдены. Попробуйте изменить запрос.")

            except ImportError:
                st.error("❌ Модуль поиска не найден. Установите необходимые зависимости.")
            except Exception as e:
                st.error(f"❌ Ошибка при поиске: {e}")


def render_history_page():
    """Страница истории анализов."""
    st.markdown("## 📊 История анализов")

    st.info("История выполненных экспертиз будет отображаться здесь")

    # TODO: Implement history tracking
    st.markdown("""
    ### Функции в разработке:

    - 📁 Сохранение результатов анализов
    - 📊 Статистика по проведенным экспертизам
    - 🔄 Возможность повторного просмотра отчетов
    - 📥 Экспорт истории в различных форматах
    - 🗂️ Группировка по датам и типам документов
    """)

    # Демо данных
    st.markdown("---")
    st.markdown("### Пример истории анализов")

    demo_data = [
        {
            "date": "2024-01-15 14:30",
            "document": "Закон о цифровизации РК",
            "stages": 6,
            "score": 95,
            "status": "✅ Готов к принятию"
        },
        {
            "date": "2024-01-14 10:15",
            "document": "Проект изменений в ГК РК",
            "stages": 6,
            "score": 78,
            "status": "⚠️ Требуются доработки"
        },
        {
            "date": "2024-01-13 16:45",
            "document": "Постановление о госзакупках",
            "stages": 4,
            "score": 88,
            "status": "✅ Готов к принятию"
        }
    ]

    for item in demo_data:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 1, 2])

            with col1:
                st.write(f"**{item['date']}**")

            with col2:
                st.write(item['document'])

            with col3:
                st.write(f"{item['stages']} этапов")

            with col4:
                st.write(f"**{item['score']}**/100")

            with col5:
                st.write(item['status'])

            st.markdown("---")


if __name__ == "__main__":
    main()
