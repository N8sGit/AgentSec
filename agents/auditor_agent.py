# agents/auditor_agent.py
from agents.agent_base import AgentSecBaseAgent
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import verify_signature  # Import the signature verification function
from security.permissions import get_clearance_level
from security.log_chain import log_action

class AuditorAgent(AgentSecBaseAgent):
    """Auditor Agent responsible for verifying and relaying commands."""

    def __init__(self):
        super().__init__('auditor_agent')

    async def on_message(self, message, ctx: MessageContext):
        """Handle incoming messages from CoreAgent."""
        
        # Verify the signature in the message
        if not verify_signature(message):
            print("Signature verification failed. Discarding command.")
            return

        # Extract the command content from the verified message
        decrypted_command = message["message"]

        # Verify permissions
        if not self.has_permission(required_level=2):
            print("Unauthorized command from CoreAgent.")
            return

        # Log the action
        log_action(self.id, 'Verified and relayed command to EdgeAgent.')

        # Send the command to EdgeAgent (no need to re-encrypt, assuming signature is sufficient)
        await self.send_message(
            message=decrypted_command,
            recipient=AgentId("edge_agent_one", "default")
        )