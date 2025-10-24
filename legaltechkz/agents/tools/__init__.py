"""
Инструменты для агентов
"""

from legaltechkz.agents.tools.base_tool import BaseTool
from legaltechkz.agents.tools.adilet_search_tool import AdiletSearchTool
from legaltechkz.agents.tools.document_fetch_tool import DocumentFetchTool
from legaltechkz.agents.tools.reference_extractor_tool import ReferenceExtractorTool

__all__ = [
    "BaseTool",
    "AdiletSearchTool",
    "DocumentFetchTool",
    "ReferenceExtractorTool",
]
