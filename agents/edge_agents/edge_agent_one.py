# agents/edge_agents/edge_agent_one.py
from agents.agent_base import AgentSecBaseAgent
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import verify_signature
from security.log_chain import log_action
import time

class EdgeAgent(AgentSecBaseAgent):
    """Edge Agent responsible for executing tasks and reporting results."""

    def __init__(self, agent_id: str):
        super().__init__(agent_id=agent_id, description="Executes tasks and reports results")
        self.agent_id = agent_id

    async def on_message(self, message, ctx: MessageContext):
        """Handle incoming structured messages."""
        # Check if the message is in the expected structure
        if not isinstance(message, dict):
            log_action(self.id, "Invalid message format received. Expected a dictionary.")
            print(f"{self.id}: Invalid message format received.")
            return

        # Verify the signature
        if not verify_signature(message):
            log_action(self.id, "Signature verification failed.")
            print(f"{self.id}: Signature verification failed.")
            return

        # Log and execute the task
        log_action(self.id, f"Received verified message: {message['message']}")
        print(f"{self.id}: Received verified message: {message['message']}")

        # Perform the task
        await self.perform_task(message)

    async def perform_task(self, message: dict):
        """Perform the specified task."""
        command = message["message"]
        print(f"{self.agent_id} performing task: {command}")

        # Log task execution
        log_action(self.agent_id, f"Task executed: {command}")

        # Create structured result data
        result = {
            "message": f"Result of task '{command}' completed by {self.agent_id}",
            "timestamp": int(time.time()),
            "sender": self.agent_id,
        }

        # Send result back to the Auditor Agent
        await self.send_data_up(result)

    async def send_data_up(self, data: dict):
        """Send data upward to the AuditorAgent."""
        log_action(self.id, f"Sending data to AuditorAgent: {data['message']}")

        # Send the structured data
        recipient_id = AgentId(type="auditor_agent", key="default")
        await self.send_message(
            message=data,
            recipient=recipient_id
        )