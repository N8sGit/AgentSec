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

    async def on_unhandled_message(self, message: DataMessage, ctx: MessageContext) -> None:
        """
        Handle unhandled messages.

        Args:
            message: The message received by the agent.
            ctx (MessageContext): The context of the message.
        """
        log_action(self.agent_id, f"Unhandled message: {message}")
        print(f"Unhandled message received by {self.agent_id}: {message}")