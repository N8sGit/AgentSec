from autogen_core.base import MessageContext
from autogen_core.components import RoutedAgent
from security.log_chain import log_action
from messages.messages import DataMessage


class AgentSecBaseAgent(RoutedAgent):
    """Base class for agents with routing and security features."""

    def __init__(self, description: str):
        """
        Initialize the AgentSecBaseAgent.

        Args:
            description (str): A description of the agent's purpose.
        """
        super().__init__(description)

    def has_permission(self, required_level: int) -> bool:
        """
        Check if the agent has the required clearance level.

        Args:
            required_level (int): The clearance level required to perform the action.

        Returns:
            bool: True if the agent has sufficient clearance, False otherwise.
        """
        # Clearance level logic is removed unless strictly required for data.
        raise NotImplementedError("Clearance level checks are no longer implemented.")

    async def on_unhandled_message(self, message: DataMessage, ctx: MessageContext) -> None:
        """
        Handle unhandled messages.

        Args:
            message: The message received by the agent.
            ctx (MessageContext): The context of the message.
        """
        log_action(self.agent_id, f"Unhandled message: {message}")
        print(f"Unhandled message received by {self.agent_id}: {message}")