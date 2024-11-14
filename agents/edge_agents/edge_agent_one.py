# agents/edge_agent.py
from agents.agent_base import AgentSecBaseAgent
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import verify_signature
from security.log_chain import log_action

class EdgeAgent(AgentSecBaseAgent):
    """Edge Agent responsible for executing tasks."""

    def __init__(self, agent_id: str):
        super().__init__(agent_id)

    async def on_message(self, message, ctx: MessageContext):
        """Handle incoming messages and execute tasks."""

        # Verify the signature in the message
        if not verify_signature(message):
            print(f"Signature verification failed for command in {self.id}.")
            return

        # Extract the command content from the verified message
        command = message["message"]

        # Perform the task
        await self.perform_task(command)

        # Log the action
        log_action(self.id, f'Executed task: {command}')

    async def perform_task(self, command: str):
        """Perform the specified task."""
        print(f"{self.id} performing task: {command}")

    async def send_data_up(self, data: str):
        """Send data upward without it being considered as an instruction."""
        # In this example, sending data up without encryption or classification handling
        await self.send_message(
            message=data,
            recipient=AgentId("auditor_agent", "default")
        )