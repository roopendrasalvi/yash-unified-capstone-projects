"""
Agent Factory
Factory pattern for creating and managing AI agents
"""

from typing import Dict, Any, Optional
from .classification_agent import ClassificationAgent
from .birthday_agent import BirthdayAgent
from .actionable_agent import ActionableAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from config.config_loader import get_model_config
import litellm
import logging

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating and managing AI agents"""
    
    def __init__(self):
        """Initialize the Agent Factory"""
        self.model_config = get_model_config()
        self.agents = {}
        self.model_client = None
        
        logger.info("Agent Factory initialized")
    
    def get_model_client(self) -> Any:
        """
        Get or create the model client
        
        Returns:
            Model client instance
        """
        if self.model_client is None:
            # Create LiteLLM client
            self.model_client = litellm.LiteLLM()
            logger.info("Model client created")
        
        return self.model_client
    
    def create_classification_agent(self) -> ClassificationAgent:
        """
        Create a Classification Agent
        
        Returns:
            ClassificationAgent instance
        """
        if "classification" not in self.agents:
            model_client = self.get_model_client()
            self.agents["classification"] = ClassificationAgent(model_client)
            logger.info("Classification Agent created")
        
        return self.agents["classification"]
    
    def create_birthday_agent(self) -> BirthdayAgent:
        """
        Create a Birthday Agent
        
        Returns:
            BirthdayAgent instance
        """
        if "birthday" not in self.agents:
            model_client = self.get_model_client()
            self.agents["birthday"] = BirthdayAgent(model_client)
            logger.info("Birthday Agent created")
        
        return self.agents["birthday"]
    
    def create_actionable_agent(self) -> ActionableAgent:
        """
        Create an Actionable Agent
        
        Returns:
            ActionableAgent instance
        """
        if "actionable" not in self.agents:
            model_client = self.get_model_client()
            self.agents["actionable"] = ActionableAgent(model_client)
            logger.info("Actionable Agent created")
        
        return self.agents["actionable"]
    
    def create_team(
        self,
        agent_types: Optional[list] = None,
        max_messages: int = 5
    ) -> SelectorGroupChat:
        """
        Create a team of agents
        
        Args:
            agent_types: List of agent types to include (default: all)
            max_messages: Maximum number of messages in conversation
            
        Returns:
            SelectorGroupChat team instance
        """
        if agent_types is None:
            agent_types = ["classification", "birthday", "actionable"]
        
        # Create agents
        agents_list = []
        
        for agent_type in agent_types:
            if agent_type == "classification":
                agent = self.create_classification_agent()
                agents_list.append(agent.agent)
            elif agent_type == "birthday":
                agent = self.create_birthday_agent()
                agents_list.append(agent.agent)
            elif agent_type == "actionable":
                agent = self.create_actionable_agent()
                agents_list.append(agent.agent)
        
        # Create termination condition
        termination = MaxMessageTermination(max_messages=max_messages)
        
        # Create team
        model_client = self.get_model_client()
        team = SelectorGroupChat(
            agents_list,
            model_client=model_client,
            termination_condition=termination
        )
        
        logger.info(f"Agent team created with {len(agents_list)} agents")
        return team
    
    def get_agent(self, agent_type: str) -> Any:
        """
        Get an existing agent or create a new one
        
        Args:
            agent_type: Type of agent to get
            
        Returns:
            Agent instance
        """
        if agent_type == "classification":
            return self.create_classification_agent()
        elif agent_type == "birthday":
            return self.create_birthday_agent()
        elif agent_type == "actionable":
            return self.create_actionable_agent()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    def reset_agents(self):
        """Reset all agents"""
        self.agents.clear()
        self.model_client = None
        logger.info("All agents reset")

