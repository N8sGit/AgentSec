# agents/agent_base.py
from abc import ABC, abstractmethod
from autogen_core.base import BaseAgent, MessageContext
from security.permissions import get_clearance_level

class AgentSecBaseAgent(BaseAgent, ABC):
    """Base class for agents with security features."""

    def __init__(self, description: str, agent_id: str):
        """
        Initialize the AgentSecBaseAgent.

        Args:
            description (str): A description of the agent's purpose.
            agent_id (str): A unique identifier for the agent.
        """
        super().__init__(description=description)  # Pass description to BaseAgent
        self.agent_id = agent_id  # Store agent_id locally for agent-specific logic
        self.clearance_level = self.get_clearance_level()  # Retrieve the clearance level for this agent

    @abstractmethod
    async def on_message(self, message, ctx: MessageContext):
        """
        Handle incoming messages. Must be implemented by subclasses.
        
        Args:
            message: The message received by the agent.
            ctx (MessageContext): The context of the message.
        """
        pass

    def get_clearance_level(self) -> int:
        """
        Retrieve the agent's clearance level.
        
        Returns:
            int: The clearance level of the agent.
        """
        return get_clearance_level(self.agent_id)

    def has_permission(self, required_level: int) -> bool:
        """
        Check if the agent has the required clearance level.

        Args:
            required_level (int): The clearance level required to perform the action.

        Returns:
            bool: True if the agent has sufficient clearance, False otherwise.
        """
        return self.clearance_level >= required_level