import logging
from agents.agent_base import AgentSecBaseAgent
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import verify_signature
from security.log_chain import log_action

class AuditorAgent(AgentSecBaseAgent):
    """Auditor Agent responsible for verifying and relaying commands."""

    def __init__(self):
        super().__init__('auditor_agent')

    async def on_message(self, message, ctx: MessageContext):
        """Handle incoming structured messages."""
        # Log raw input
        log_action(self.id, f"Raw message received: {message}")
        print(f"{self.id}: Raw message received: {message}")
        print(f"{self.id}: Context received: {ctx}")

        # Check if the message is a dictionary
        if not isinstance(message, dict):
            log_action(self.id, f"Invalid message type: {type(message)}. Expected dictionary.")
            print(f"{self.id}: Invalid message type: {type(message)}. Expected dictionary.")
            return

        # Log message keys
        log_action(self.id, f"Message keys: {list(message.keys())}")
        print(f"{self.id}: Message keys: {list(message.keys())}")

        # Validate required keys
        required_keys = {"message", "timestamp", "signature", "clearance_lvl", "sender"}
        missing_keys = required_keys - message.keys()
        if missing_keys:
            log_action(self.id, f"Missing keys: {missing_keys}")
            print(f"{self.id}: Missing keys: {missing_keys}")
            return

        # Verify the signature
        if not verify_signature(message):
            log_action(self.id, "Signature verification failed.")
            print(f"{self.id}: Signature verification failed.")
            return

        # Log successful validation
        log_action(self.id, f"Message verified: {message}")
        print(f"{self.id}: Message verified: {message}")

        # Relay the message to the EdgeAgent
        recipient = AgentId(type="edge_agent", key="default")
        await self.send_message(message, recipient)
        log_action(self.id, f"Message relayed to {recipient}.")
        print(f"{self.id}: Message relayed to {recipient}.")