"""
Agent module for the ANUS framework.

This module contains various agent implementations:
- BaseAgent: Abstract base class for all agents
- ReactAgent: Agent with reasoning capabilities
- ToolAgent: Agent with tool execution capabilities
- HybridAgent: Agent that can switch between single and multi-agent modes
"""

from legaltechkz.core.agent.base_agent import BaseAgent
from legaltechkz.core.agent.react_agent import ReactAgent
from legaltechkz.core.agent.tool_agent import ToolAgent
from legaltechkz.core.agent.hybrid_agent import HybridAgent

__all__ = ["BaseAgent", "ReactAgent", "ToolAgent", "HybridAgent"] 