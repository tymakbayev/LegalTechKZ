"""
UI module for LegalTechKZ.

This module contains user interface components:
- CLI: Command-line interface
- Web Integration: Streamlit web interface integration
"""

from legaltechkz.ui.cli import CLI
from legaltechkz.ui.web_integration import (
    WebExpertiseController,
    ExpertiseProgress,
    StageResult,
    get_controller
)

__all__ = [
    "CLI",
    "WebExpertiseController",
    "ExpertiseProgress",
    "StageResult",
    "get_controller"
] 