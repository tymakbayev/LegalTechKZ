"""
Completeness Validator для проверки полноты анализа НПА.

Гарантирует, что ни одна статья не пропущена при экспертизе.
"""

from typing import List, Set, Dict, Any
from dataclasses import dataclass
import logging

from legaltechkz.expertise.document_parser import DocumentFragment

logger = logging.getLogger("legaltechkz.expertise.completeness_validator")


@dataclass
class AnalysisResult:
    """Результат анализа одного фрагмента."""

    fragment_id: str  # ID фрагмента (например, "article_15")
    fragment_number: str  # Номер статьи/пункта
    analysis_completed: bool  # Был ли завершён анализ
    analysis_data: Dict[str, Any]  # Данные анализа


class CompletenessValidator:
    """
    Валидатор полноты анализа НПА.

    Отслеживает какие статьи были проанализированы и выявляет пропущенные.
    """

    def __init__(self, fragments: List[DocumentFragment]):
        """
        Инициализация валидатора.

        Args:
            fragments: Список всех фрагментов документа из парсера.
        """
        self.fragments = fragments
        self.articles = [f for f in fragments if f.type == 'article']

        # Создаём чеклист всех статей
        self.checklist: Dict[str, bool] = {
            f"article_{article.number}": False
            for article in self.articles
        }

        # Результаты анализа
        self.analysis_results: Dict[str, AnalysisResult] = {}

        logger.info(f"Инициализирован валидатор. Статей в чеклисте: {len(self.checklist)}")

    def mark_analyzed(self, article_number: str, analysis_data: Dict[str, Any] = None) -> None:
        """
        Пометить статью как проанализированную.

        Args:
            article_number: Номер статьи.
            analysis_data: Данные анализа.
        """
        fragment_id = f"article_{article_number}"

        if fragment_id in self.checklist:
            self.checklist[fragment_id] = True

            self.analysis_results[fragment_id] = AnalysisResult(
                fragment_id=fragment_id,
                fragment_number=article_number,
                analysis_completed=True,
                analysis_data=analysis_data or {}
            )

            logger.debug(f"Статья {article_number} помечена как проанализированная")
        else:
            logger.warning(f"Попытка пометить несуществующую статью: {article_number}")

    def get_missing_articles(self) -> List[DocumentFragment]:
        """
        Получить список пропущенных статей.

        Returns:
            Список непроанализированных статей.
        """
        missing = []

        for article in self.articles:
            fragment_id = f"article_{article.number}"
            if not self.checklist.get(fragment_id, False):
                missing.append(article)

        if missing:
            logger.warning(f"Обнаружено {len(missing)} пропущенных статей: {[a.number for a in missing]}")

        return missing

    def is_complete(self) -> bool:
        """
        Проверить, завершён ли анализ всех статей.

        Returns:
            True если все статьи проанализированы.
        """
        return all(self.checklist.values())

    def get_completion_rate(self) -> float:
        """
        Получить процент завершённости анализа.

        Returns:
            Процент от 0.0 до 1.0.
        """
        if not self.checklist:
            return 1.0

        completed = sum(1 for v in self.checklist.values() if v)
        total = len(self.checklist)

        return completed / total

    def get_completion_report(self) -> Dict[str, Any]:
        """
        Получить отчёт о полноте анализа.

        Returns:
            Словарь с детальным отчётом.
        """
        missing = self.get_missing_articles()
        completion_rate = self.get_completion_rate()

        return {
            'total_articles': len(self.articles),
            'analyzed_articles': len(self.checklist) - len(missing),
            'missing_articles': len(missing),
            'completion_rate': completion_rate,
            'completion_percentage': f"{completion_rate * 100:.1f}%",
            'is_complete': self.is_complete(),
            'missing_article_numbers': [a.number for a in missing],
            'missing_article_details': [
                {
                    'number': a.number,
                    'title': a.title,
                    'full_path': a.full_path,
                    'text_preview': a.text[:100] + '...' if len(a.text) > 100 else a.text
                }
                for a in missing
            ]
        }

    def generate_checklist_text(self) -> str:
        """
        Сгенерировать текстовый чеклист для промпта.

        Returns:
            Строка с полным оглавлением для контроля.
        """
        lines = ["=== ОГЛАВЛЕНИЕ-ЧЕКЛИСТ ДЛЯ КОНТРОЛЯ ПОЛНОТЫ АНАЛИЗА ===", ""]

        current_chapter = None

        for article in self.articles:
            # Если есть родительская глава
            if article.parent_number and article.parent_number != current_chapter:
                current_chapter = article.parent_number
                lines.append(f"\nГлава {current_chapter}:")

            # Статья с галочкой или без
            fragment_id = f"article_{article.number}"
            status = "✅" if self.checklist.get(fragment_id, False) else "⬜"
            title = f": {article.title}" if article.title else ""

            lines.append(f"{status} Статья {article.number}{title}")

        lines.append("")
        lines.append(f"Всего статей: {len(self.articles)}")
        lines.append(f"Проанализировано: {len(self.checklist) - len(self.get_missing_articles())}")
        lines.append(f"Процент завершения: {self.get_completion_rate() * 100:.1f}%")

        return "\n".join(lines)

    def validate_and_report(self) -> Dict[str, Any]:
        """
        Провести валидацию и создать полный отчёт.

        Returns:
            Отчёт с рекомендациями.
        """
        report = self.get_completion_report()

        if not report['is_complete']:
            logger.error(
                f"⚠️ АНАЛИЗ НЕПОЛНЫЙ! "
                f"Пропущено статей: {report['missing_articles']} "
                f"({', '.join(report['missing_article_numbers'])})"
            )

            report['recommendation'] = (
                "КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ: Анализ не завершён! "
                "Необходимо проанализировать пропущенные статьи для обеспечения полноты экспертизы."
            )
        else:
            logger.info("✅ Анализ завершён полностью. Все статьи обработаны.")
            report['recommendation'] = "Анализ выполнен полностью. Все статьи НПА обработаны."

        return report
