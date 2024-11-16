# agents/auditor_agent.py
from agents.agent_base import AgentSecBaseAgent
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import verify_signature  # Import the signature verification function
from security.permissions import get_clearance_level
from security.log_chain import log_action

class AuditorAgent(AgentSecBaseAgent):
    """Auditor Agent responsible for verifying and relaying commands."""
    def __init__(self, name: str, agent_id: str):
        super().__init__(name=name, description="Ensures compliance, verifies signatures, and relays authorized commands.", agent_id=agent_id)
        self.agent_id = agent_id 

    async def on_message(self, message, ctx: MessageContext):
        """Handle incoming messages from CoreAgent."""
        
        # Log receipt of the message
        log_action(self.id, f'Received message: {message}')

        # Verify the signature in the message
        if not verify_signature(message):
            log_action(self.id, "Signature verification failed. Discarding command.")
            print("Signature verification failed.")
            return

        # Extract the command content from the verified message
        decrypted_command = message.get("message", None)
        if not decrypted_command:
            log_action(self.id, "Message content missing. Discarding command.")
            print("Message content missing.")
            return

        # Verify permissions
        clearance_level = get_clearance_level(ctx.source)
        required_clearance = 2  # Example clearance level required
        if clearance_level < required_clearance:
            log_action(self.id, f"Unauthorized command from {ctx.source}. Clearance level {clearance_level} insufficient.")
            print("Unauthorized command.")
            return

        # Log the successful verification
        log_action(self.id, "Command verified successfully. Relaying to EdgeAgent.")

        # Send the command to EdgeAgent (assume signature verification suffices)
        await self.send_message(
            message=decrypted_command,
            recipient=AgentId("edge_agent_one", "default")
        )
        log_action(self.id, "Command relayed to EdgeAgent.")

    def has_permission(self, clearance_level: int, required_level: int) -> bool:
        """Check if the agent has the required permissions."""
        return clearance_level >= required_level