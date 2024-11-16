# agents/edge_agents/edge_agent_one.py
from agents.agent_base import AgentSecBaseAgent
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import verify_signature
from security.log_chain import log_action

class EdgeAgent(AgentSecBaseAgent):
    """Edge Agent responsible for executing tasks and reporting results."""
    
    def __init__(self, name: str, agent_id: str):
        super().__init__(name=name, description="Executes tasks and reports results", agent_id=agent_id)
        self.agent_id = agent_id  # Retain agent_id for potential future use

    async def on_message(self, message, ctx: MessageContext):
        """Handle incoming messages and execute tasks."""
        
        # Log receipt of the message
        log_action(self.id, f"Received message: {message}")

        # Verify the signature in the message
        if not verify_signature(message):
            log_action(self.id, f"Signature verification failed for message: {message}")
            print(f"Signature verification failed for {self.id}.")
            return

        # Extract the command content from the verified message
        command = message.get("message", None)
        if not command:
            log_action(self.id, "Message content missing. Unable to process.")
            print(f"Message content missing in {self.id}.")
            return

        # Perform the task
        await self.perform_task(command)

        # Log the execution
        log_action(self.id, f"Executed task: {command}")

    async def perform_task(self, command: str):
        """Perform the specified task."""
        # Task-specific logic here
        print(f"{self.id} performing task: {command}")

    async def send_data_up(self, data: str):
        """Send data upward to the AuditorAgent."""
        # Log the outgoing data
        log_action(self.id, f"Sending data to AuditorAgent: {data}")
        
        # Send the data upward
        await self.send_message(
            message=data,
            recipient=AgentId("auditor_agent", "default")
        )