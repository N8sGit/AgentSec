# agents/auditor_agent.py
from agents.agent_base import AgentSecBaseAgent
from autogen_core.base import MessageContext
from security.encryption_tools import decrypt_data, encrypt_data
from security.permissions import get_clearance_level
from security.blockchain import log_action

class AuditorAgent(AgentSecBaseAgent):
    """Auditor Agent responsible for verifying and relaying commands."""

    def __init__(self):
        super().__init__('auditor_agent')

    async def on_message(self, message, ctx: MessageContext):
        """Handle incoming messages from CoreAgent."""
        # Decrypt the message from CoreAgent
        decrypted_command = decrypt_data(message, self.id)
        if decrypted_command is None:
            print("AuditorAgent could not decrypt the command.")
            return

        # Verify permissions
        if not self.has_permission(required_level=2):
            print("Unauthorized command from CoreAgent.")
            return

        # Re-encrypt command for EdgeAgent
        edge_clearance_level = get_clearance_level('edge_agent_one')
        re_encrypted_command = encrypt_data(
            decrypted_command,
            edge_clearance_level,
            'edge_agent_one'
        )

        # Log the action
        log_action(self.id, 'Relayed command to EdgeAgent.')

        # Send the command to EdgeAgent
        await self.send_message(
            message=re_encrypted_command,
            recipient='edge_agent_one'
        )