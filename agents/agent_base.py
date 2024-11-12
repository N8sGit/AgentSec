# agents/agent_sec_base_agent.py
from abc import ABC, abstractmethod
from autogen_core.base import MessageContext
from autogen_core.components import RoutedAgent
from security.permissions import get_clearance_level

class AgentSecBaseAgent(RoutedAgent, ABC):
    """Base class for agents with security features."""

    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.clearance_level = self.get_clearance_level()

    @abstractmethod
    async def on_message(self, message, ctx: MessageContext):
        """Handle incoming messages. Must be implemented by subclasses."""
        pass

    def get_clearance_level(self) -> int:
        """Retrieve the agent's clearance level."""
        return get_clearance_level(self.id)

    def has_permission(self, required_level: int) -> bool:
        """Check if the agent has the required clearance level."""
        return self.clearance_level >= required_level