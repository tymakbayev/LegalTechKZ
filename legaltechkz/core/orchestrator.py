"""
Orchestrator module for the LegalTechKZ framework.

This module contains the agent orchestration system that manages agent
lifecycle and coordinates task execution across multiple agents.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import yaml
import os
import time
import random

from legaltechkz.core.agent import BaseAgent, HybridAgent
from legaltechkz.core.memory import ShortTermMemory, LongTermMemory

# Create logger for the orchestrator
logger = logging.getLogger("legaltechkz.orchestrator")

class AgentOrchestrator:
    """
    Coordinates multiple agents and manages their lifecycle.

    This class is responsible for:
    - Loading configuration
    - Creating and initializing agents
    - Routing tasks to appropriate agents
    - Managing agent resources
    - Collecting and aggregating results
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize an AgentOrchestrator instance.
        
        Args:
            config_path: Path to the configuration file.
        """
        self.config = self._load_config(config_path)
        self.agents: Dict[str, BaseAgent] = {}
        self.primary_agent = self._create_primary_agent()
        self.last_result: Dict[str, Any] = {}
        self.task_history: List[Dict[str, Any]] = []

        logger.info("LegalTechKZ Orchestrator initialized successfully")
    
    def execute_task(self, task: str, mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task using an appropriate agent.
        
        Args:
            task: The task description to execute.
            mode: Execution mode ("single" or "multi"). If None, uses the config default.
            
        Returns:
            The execution result.
        """
        # Use config default if mode not specified
        if mode is None:
            mode = self.config.get("agent", {}).get("mode", "single")
        
        start_time = time.time()

        # Log the task
        if mode == "multi":
            logger.info(f"Executing task with multiple agents: {task}")
        else:
            logger.info(f"Executing task: {task}")
        
        # Execute the task with the primary agent
        result = self.primary_agent.execute(task, mode=mode)
        
        # Record execution time
        execution_time = time.time() - start_time
        
        # Create a task record
        task_record = {
            "task": task,
            "mode": mode,
            "start_time": start_time,
            "execution_time": execution_time,
            "status": "completed",
            "result": result
        }
        
        # Add to task history
        self.task_history.append(task_record)
        
        # Update last result
        self.last_result = result
        
        # Log completion
        logger.info(f"Task completed in {execution_time:.2f}s")
        
        return result
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            A list of agent descriptions.
        """
        agent_list = []
        
        # Add primary agent
        agent_list.append({
            "id": self.primary_agent.id,
            "name": self.primary_agent.name,
            "type": type(self.primary_agent).__name__,
            "primary": True
        })
        
        # Add other agents
        for name, agent in self.agents.items():
            if agent.id != self.primary_agent.id:
                agent_list.append({
                    "id": agent.id,
                    "name": agent.name,
                    "type": type(agent).__name__,
                    "primary": False
                })
        
        if len(agent_list) > 3:
            logger.debug(f"Managing {len(agent_list)} agents")

        return agent_list
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the history of executed tasks.
        
        Args:
            limit: Maximum number of history items to return.
            
        Returns:
            A list of task history records.
        """
        if limit > 50:
            logger.warning(f"Requesting {limit} history items may impact performance")

        return self.task_history[-limit:]
    
    def get_last_result(self) -> Dict[str, Any]:
        """
        Get the result of the last executed task.
        
        Returns:
            The last execution result.
        """
        return self.last_result
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the configuration file.
            
        Returns:
            The loaded configuration.
        """
        # Default configuration
        default_config = {
            "agent": {
                "name": "legal_expert",
                "mode": "single",
                "max_iterations": 10,
                "complexity_threshold": 7
            },
            "memory": {
                "short_term": {
                    "capacity": 1000,
                    "ttl": 3600
                },
                "long_term": {
                    "enabled": True,
                    "storage_path": None,
                    "index_in_memory": True
                }
            },
            "models": {
                "default": {
                    "provider": "openai",
                    "model": "gpt-4",
                    "temperature": 0.0
                }
            },
            "tools": {
                "enabled": []
            }
        }
        
        # Check if config file exists
        if not os.path.exists(config_path):
            logger.warning(f"Config file {config_path} not found. Using default configuration.")
            return default_config
        
        try:
            # Load the config file
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            
            # Merge with default config
            merged_config = self._merge_configs(default_config, config)

            logger.info("Configuration loaded successfully")
            if merged_config.get("agent", {}).get("mode") == "multi":
                logger.info("Multi-agent mode enabled")

            return merged_config
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            logger.info("Using default configuration")
            return default_config
    
    def _merge_configs(self, default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries.
        
        Args:
            default: Default configuration.
            override: Override configuration.
            
        Returns:
            The merged configuration.
        """
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_primary_agent(self) -> HybridAgent:
        """
        Create the primary agent based on configuration.
        
        Returns:
            A HybridAgent instance.
        """
        # Get agent config
        agent_config = self.config.get("agent", {})
        name = agent_config.get("name", "anus")
        mode = agent_config.get("mode", "single")
        max_iterations = agent_config.get("max_iterations", 10)
        complexity_threshold = agent_config.get("complexity_threshold", 7)
        
        # Get tools config
        tools_config = self.config.get("tools", {})
        enabled_tools = tools_config.get("enabled", [])
        
        # Create memories
        short_term_memory = self._create_short_term_memory()
        long_term_memory = self._create_long_term_memory()
        
        # Create the agent
        agent = HybridAgent(
            name=name,
            max_iterations=max_iterations,
            tools=enabled_tools,
            mode=mode,
            complexity_threshold=complexity_threshold,
            short_term_memory=short_term_memory,
            long_term_memory=long_term_memory
        )
        
        logger.info(f"Primary agent created with {len(enabled_tools)} tools available")

        # Create specialized agents if in multi mode
        if mode == "multi" or mode == "auto":
            self._create_specialized_agents(agent)
            logger.info("Specialized agents initialized")
        
        # Register the agent
        self.agents[name] = agent
        
        return agent
    
    def _create_short_term_memory(self) -> ShortTermMemory:
        """
        Create a short-term memory instance based on configuration.
        
        Returns:
            A ShortTermMemory instance.
        """
        memory_config = self.config.get("memory", {}).get("short_term", {})
        capacity = memory_config.get("capacity", 1000)
        ttl = memory_config.get("ttl", 3600)
        
        logger.debug(f"Initializing short-term memory with capacity {capacity}")
        return ShortTermMemory(capacity=capacity, ttl=ttl)
    
    def _create_long_term_memory(self) -> Optional[LongTermMemory]:
        """
        Create a long-term memory instance based on configuration.
        
        Returns:
            A LongTermMemory instance, or None if disabled.
        """
        memory_config = self.config.get("memory", {}).get("long_term", {})
        enabled = memory_config.get("enabled", True)
        
        if not enabled:
            logger.info("Long-term memory disabled")
            return None

        storage_path = memory_config.get("storage_path")
        index_in_memory = memory_config.get("index_in_memory", True)

        if storage_path:
            logger.debug(f"Long-term memory storage path: {storage_path}")
        else:
            logger.debug("Using default long-term memory storage location")
        
        return LongTermMemory(storage_path=storage_path, index_in_memory=index_in_memory)
    
    def _create_specialized_agents(self, primary_agent: HybridAgent) -> None:
        """
        Create specialized agents for multi-agent mode.
        
        Args:
            primary_agent: The primary HybridAgent instance.
        """
        # Default specialized agent roles
        default_roles = ["researcher", "planner", "executor", "critic"]
        
        # Get specialized agent configurations
        specialized_config = self.config.get("specialized_agents", {})
        roles = specialized_config.get("roles", default_roles)
        
        # Create each specialized agent
        for role in roles:
            role_config = specialized_config.get(role, {})
            
            # Default configuration for the role
            default_role_config = {
                "name": f"{role}-agent",
                "max_iterations": primary_agent.max_iterations,
                "tools": self.config.get("tools", {}).get("enabled", [])
            }
            
            # Merge with role-specific config
            merged_config = self._merge_configs(default_role_config, role_config)
            
            # Add to the primary agent
            primary_agent.add_specialized_agent(role, merged_config)

            logger.debug(f"Added {role} agent")

        logger.info(f"Initialized {len(roles)} specialized agents")
        if len(roles) > 5:
            logger.warning(f"Managing {len(roles)} agents may impact performance") 