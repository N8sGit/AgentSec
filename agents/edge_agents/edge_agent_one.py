# agents/edge_agent.py
from agents.agent_base import AgentSecBaseAgent
from autogen_core.base import MessageContext
from security.encryption_tools import decrypt_data, encrypt_data
from security.blockchain import log_action

class EdgeAgent(AgentSecBaseAgent):
    """Edge Agent responsible for executing tasks."""

    def __init__(self, agent_id: str):
        super().__init__(agent_id)

    async def on_message(self, message, ctx: MessageContext):
        """Handle incoming messages and execute tasks."""
        # Decrypt the command
        command = decrypt_data(message, self.id)
        if command is None:
            print(f"{self.id} does not have clearance to execute this command.")
            return

        # Perform the task
        await self.perform_task(command)

        # Log the action
        log_action(self.id, f'Executed task: {command}')

    async def perform_task(self, command: str):
        """Perform the specified task."""
        print(f"{self.id} performing task: {command}")

        # After performing the task, send data back up
        data = f"Result from {self.id} for command: {command}"
        await self.send_data_up(data)

    async def send_data_up(self, data: str):
        """Send data upward without it being considered as an instruction."""
        encrypted_data = encrypt_data(data, self.clearance_level, self.id)
        # Send data back to AuditorAgent
        await self.send_message(
            message=encrypted_data,
            recipient='auditor_agent'
        )