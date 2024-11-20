# agents/core_agent.py
from agents.agent_base import AgentSecBaseAgent
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import sign_message
from security.log_chain import log_action
from security.authentication import authenticate_source
from messages.messages import InstructionMessage

class CoreAgent(AgentSecBaseAgent):
    """Core Agent responsible for processing user commands."""

    def __init__(self, agent_id: str):
        super().__init__(agent_id=agent_id, description='Responsible for issuing commands, setting the agenda, and coordinating other agents.')
        self.agent_id = agent_id

    async def on_message(self, message: InstructionMessage, ctx: MessageContext):
        """Process incoming instruction messages."""
        await self.process_command(message.content, message.token, message.clearance_lvl)

    async def process_command(self, command: str, user_token: str, clearance_lvl: int):
        if not self.authenticate(user_token):
            print("Authentication failed.")
            return

        # Sign the command
        signed_command = sign_message(command)
        
        # Add necessary metadata
        signed_command["clearance_lvl"] = clearance_lvl
        signed_command["sender"] = self.agent_id

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