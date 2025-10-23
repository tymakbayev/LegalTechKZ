"""
Models module for the ANUS framework.

This module contains language model implementations and utilities:
- BaseModel: Abstract base class for all language models
- OpenAIModel: Implementation for the OpenAI API
- ModelRouter: Dynamic model selection based on task requirements
"""

from legaltechkz.models.base import BaseModel
from legaltechkz.models.openai_model import OpenAIModel
from legaltechkz.models.model_router import ModelRouter

__all__ = ["BaseModel", "OpenAIModel", "ModelRouter"] 