# agents/core_agent.py
from agents.agent_base import AgentSecBaseAgent
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import sign_message
from security.log_chain import log_action
from security.authentication import authenticate_source
from messages.messages import InstructionMessage

class CoreAgent(AgentSecBaseAgent):
    """Core Agent responsible for processing user commands."""

    def __init__(self):
        super().__init__('core_agent')

    async def on_message(self, message: InstructionMessage, ctx: MessageContext):
        """Process incoming instruction messages."""
        await self.process_command(message.content, message.token)

    async def process_command(self, command: str, user_token: str):
        if not self.authenticate(user_token):
            print("Authentication failed.")
            return

        # Sign the command
        signed_command = sign_message(command)  # Includes message, timestamp, and signature

        # Log the action
        log_action(self.id, 'Issued command.')

        # Send the signed command to the AuditorAgent
        await self.send_message(
            message=signed_command,
            recipient=AgentId("auditor_agent", "default")
        )

    def authenticate(self, token: str) -> bool:
        """Authenticate the user token."""
        return authenticate_source(token)