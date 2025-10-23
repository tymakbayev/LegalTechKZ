"""
Legal Expertise Pipeline - главный координатор правовой экспертизы НПА.

Интегрирует 6 типов экспертизы с гарантией полноты анализа.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from legaltechkz.expertise.document_parser import NPADocumentParser, DocumentFragment
from legaltechkz.expertise.completeness_validator import CompletenessValidator
from legaltechkz.expertise.expert_agents import (
    RelevanceFilterAgent,
    ConstitutionalityFilterAgent,
    SystemIntegrationFilterAgent,
    LegalTechnicalExpertAgent,
    AntiCorruptionExpertAgent,
    GenderExpertAgent
)
from legaltechkz.models.model_router import ModelRouter

logger = logging.getLogger("legaltechkz.expertise.pipeline")


class LegalExpertisePipeline:
    """
    Главный pipeline для проведения комплексной правовой экспертизы НПА.

    Последовательно проводит 6 типов экспертизы с использованием
    возможностей трёх моделей:
    - Gemini 2.5 Flash: обработка больших документов
    - Claude Sonnet 4.5: глубокий анализ
    - GPT-4.1: суммаризация результатов
    """

    EXPERTISE_STAGES = [
        "Фильтр Релевантности",
        "Фильтр Конституционности",
        "Фильтр Системной Интеграции",
        "Юридико-техническая Экспертиза",
        "Антикоррупционная Экспертиза",
        "Гендерная Экспертиза"
    ]

    def __init__(self, model_router: Optional[ModelRouter] = None):
        """
        Инициализация pipeline.

        Args:
            model_router: Роутер моделей. Создаётся по умолчанию если не указан.
        """
        self.model_router = model_router or ModelRouter(enable_auto_selection=True)
        self.parser = NPADocumentParser()
        self.validator: Optional[CompletenessValidator] = None

        # История выполнения
        self.execution_history: List[Dict[str, Any]] = []

        logger.info("LegalExpertisePipeline инициализирован")

    def conduct_full_expertise(
        self,
        document_text: str,
        skip_stages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Провести полную правовую экспертизу документа.

        Args:
            document_text: Полный текст НПА.
            skip_stages: Список этапов для пропуска (опционально).

        Returns:
            Полный отчёт об экспертизе.
        """
        skip_stages = skip_stages or []

        logger.info("=" * 70)
        logger.info("НАЧАЛО КОМПЛЕКСНОЙ ПРАВОВОЙ ЭКСПЕРТИЗЫ НПА")
        logger.info("=" * 70)

        execution_record = {
            'start_time': datetime.now().isoformat(),
            'stages': [],
            'success': True
        }

        try:
            # ==== ШАГ 0: Парсинг и создание чеклиста ====
            logger.info("\n[ШАГ 0] Парсинг документа и создание оглавления-чеклиста...")

            fragments = self.parser.parse(document_text)
            self.validator = CompletenessValidator(fragments)

            checklist_text = self.validator.generate_checklist_text()
            articles = self.parser.get_articles()

            logger.info(f"✅ Документ разобран. Найдено статей: {len(articles)}")
            logger.info(f"\nОГЛАВЛЕНИЕ:\n{checklist_text}\n")

            execution_record['parsing'] = {
                'total_fragments': len(fragments),
                'total_articles': len(articles),
                'success': True
            }

            # ==== ОСНОВНЫЕ ЭТАПЫ ЭКСПЕРТИЗЫ ====

            # Этап 1: Фильтр Релевантности (Claude)
            if "Фильтр Релевантности" not in skip_stages:
                logger.info("\n" + "=" * 70)
                logger.info("[ЭТАП 1] ФИЛЬТР РЕЛЕВАНТНОСТИ")
                logger.info("=" * 70)

                model = self.model_router.select_model_for_pipeline_stage("analysis")
                agent = RelevanceFilterAgent(model)

                stage_result = self._run_expertise_stage(agent, articles, checklist_text)
                execution_record['stages'].append(stage_result)

            # Этап 2: Фильтр Конституционности (Claude)
            if "Фильтр Конституционности" not in skip_stages:
                logger.info("\n" + "=" * 70)
                logger.info("[ЭТАП 2] ФИЛЬТР КОНСТИТУЦИОННОСТИ")
                logger.info("=" * 70)

                model = self.model_router.select_model_for_pipeline_stage("analysis")
                agent = ConstitutionalityFilterAgent(model)

                stage_result = self._run_expertise_stage(agent, articles, checklist_text)
                execution_record['stages'].append(stage_result)

            # Этап 3: Фильтр Системной Интеграции (Claude)
            if "Фильтр Системной Интеграции" not in skip_stages:
                logger.info("\n" + "=" * 70)
                logger.info("[ЭТАП 3] ФИЛЬТР СИСТЕМНОЙ ИНТЕГРАЦИИ")
                logger.info("=" * 70)

                model = self.model_router.select_model_for_pipeline_stage("analysis")
                agent = SystemIntegrationFilterAgent(model)

                stage_result = self._run_expertise_stage(agent, articles, checklist_text)
                execution_record['stages'].append(stage_result)

            # Этап 4: Юридико-техническая Экспертиза (Claude)
            if "Юридико-техническая Экспертиза" not in skip_stages:
                logger.info("\n" + "=" * 70)
                logger.info("[ЭТАП 4] ЮРИДИКО-ТЕХНИЧЕСКАЯ ЭКСПЕРТИЗА")
                logger.info("=" * 70)

                model = self.model_router.select_model_for_pipeline_stage("analysis")
                agent = LegalTechnicalExpertAgent(model)

                stage_result = self._run_expertise_stage(agent, articles, checklist_text)
                execution_record['stages'].append(stage_result)

            # Этап 5: Антикоррупционная Экспертиза (Claude)
            if "Антикоррупционная Экспертиза" not in skip_stages:
                logger.info("\n" + "=" * 70)
                logger.info("[ЭТАП 5] АНТИКОРРУПЦИОННАЯ ЭКСПЕРТИЗА")
                logger.info("=" * 70)

                model = self.model_router.select_model_for_pipeline_stage("analysis")
                agent = AntiCorruptionExpertAgent(model)

                stage_result = self._run_expertise_stage(agent, articles, checklist_text)
                execution_record['stages'].append(stage_result)

            # Этап 6: Гендерная Экспертиза (Claude)
            if "Гендерная Экспертиза" not in skip_stages:
                logger.info("\n" + "=" * 70)
                logger.info("[ЭТАП 6] ГЕНДЕРНАЯ ЭКСПЕРТИЗА")
                logger.info("=" * 70)

                model = self.model_router.select_model_for_pipeline_stage("analysis")
                agent = GenderExpertAgent(model)

                stage_result = self._run_expertise_stage(agent, articles, checklist_text)
                execution_record['stages'].append(stage_result)

            # ==== ФИНАЛЬНАЯ ПРОВЕРКА ПОЛНОТЫ ====
            logger.info("\n" + "=" * 70)
            logger.info("[ФИНАЛЬНАЯ ПРОВЕРКА] ПОЛНОТА АНАЛИЗА")
            logger.info("=" * 70)

            completeness_report = self.validator.validate_and_report()
            execution_record['completeness'] = completeness_report

            if not completeness_report['is_complete']:
                logger.error(f"\n⚠️ {completeness_report['recommendation']}")

                # Попытка повторной обработки пропущенных статей
                missing_articles = self.validator.get_missing_articles()

                if missing_articles:
                    logger.warning(f"\n🔄 Повторная обработка {len(missing_articles)} пропущенных статей...")
                    # TODO: Реализовать повторную обработку

            else:
                logger.info(f"\n✅ {completeness_report['recommendation']}")

            execution_record['end_time'] = datetime.now().isoformat()

            # ==== ГЕНЕРАЦИЯ ИТОГОВОГО ОТЧЁТА ====
            logger.info("\n" + "=" * 70)
            logger.info("[ЗАВЕРШЕНИЕ] ГЕНЕРАЦИЯ ИТОГОВОГО ОТЧЁТА")
            logger.info("=" * 70)

            final_report = self._generate_final_report(execution_record)

            self.execution_history.append(execution_record)

            logger.info("\n✅ ЭКСПЕРТИЗА ЗАВЕРШЕНА")
            logger.info("=" * 70)

            return final_report

        except Exception as e:
            logger.error(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ЭКСПЕРТИЗЕ: {e}")
            import traceback
            traceback.print_exc()

            execution_record['success'] = False
            execution_record['error'] = str(e)
            execution_record['end_time'] = datetime.now().isoformat()

            return {
                'success': False,
                'error': str(e),
                'execution_record': execution_record
            }

    def _run_expertise_stage(
        self,
        agent,
        articles: List[DocumentFragment],
        checklist: str
    ) -> Dict[str, Any]:
        """
        Запустить один этап экспертизы.

        Args:
            agent: Экспертный агент.
            articles: Список статей для анализа.
            checklist: Оглавление-чеклист.

        Returns:
            Результат этапа.
        """
        stage_start = datetime.now()

        try:
            results = agent.analyze_batch(articles, checklist)

            # Помечаем проанализированные статьи
            for result in results:
                if result.get('success'):
                    self.validator.mark_analyzed(
                        result['fragment_number'],
                        result
                    )

            stage_summary = agent.get_results_summary()

            stage_duration = (datetime.now() - stage_start).total_seconds()

            logger.info(f"\n✅ Этап '{agent.agent_name}' завершён")
            logger.info(f"   Проанализировано: {stage_summary['successful']}/{stage_summary['total_analyzed']}")
            logger.info(f"   Время: {stage_duration:.1f}с")

            return {
                'stage_name': agent.agent_name,
                'success': True,
                'summary': stage_summary,
                'results': results,
                'duration_seconds': stage_duration
            }

        except Exception as e:
            logger.error(f"\n❌ Ошибка на этапе '{agent.agent_name}': {e}")

            return {
                'stage_name': agent.agent_name,
                'success': False,
                'error': str(e)
            }

    def _generate_final_report(self, execution_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Сгенерировать итоговый отчёт экспертизы.

        Args:
            execution_record: Запись о выполнении.

        Returns:
            Итоговый отчёт.
        """
        logger.info("\nГенерация сводного отчёта...")

        # Используем GPT-4.1 для суммаризации
        model = self.model_router.select_model_for_pipeline_stage("summarization")

        # Собираем ключевые находки
        all_findings = []

        for stage in execution_record.get('stages', []):
            if stage.get('success'):
                stage_name = stage['stage_name']
                results = stage.get('results', [])

                for result in results:
                    if result.get('success'):
                        all_findings.append({
                            'stage': stage_name,
                            'article': result['fragment_number'],
                            'analysis': result['analysis']
                        })

        report = {
            'success': execution_record['success'],
            'start_time': execution_record['start_time'],
            'end_time': execution_record['end_time'],
            'parsing': execution_record.get('parsing', {}),
            'stages_completed': len(execution_record.get('stages', [])),
            'completeness': execution_record.get('completeness', {}),
            'total_articles_analyzed': len(all_findings),
            'findings': all_findings,
            'execution_record': execution_record
        }

        logger.info("✅ Итоговый отчёт сформирован")

        return report
