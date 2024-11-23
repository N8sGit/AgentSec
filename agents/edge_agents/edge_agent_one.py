from agents.agent_base import AgentSecBaseAgent
from autogen_core.components import rpc, event, DefaultTopicId
from autogen_core.base import MessageContext
from security.signature_tools import verify_signature
from security.log_chain import log_action
from messages.messages import InstructionMessage, DataMessage
import time

class EdgeAgent(AgentSecBaseAgent):
    """Edge Agent responsible for executing tasks and reporting results."""

    def __init__(self, agent_id: str):
        super().__init__(description="Executes tasks and reports results")
        self.agent_id = agent_id

    @rpc
    async def handle_instruction(self, message: InstructionMessage, ctx: MessageContext) -> None:
        """Handle incoming instructions."""
        log_action(self.agent_id, f"Instruction received: {message}")

        # Verify the signature
        if not verify_signature(message):
            log_action(self.agent_id, "Signature verification failed.")
            return

        log_action(self.agent_id, f"Instruction verified: {message.message}")
        await self.perform_task(message)

    async def perform_task(self, instruction: InstructionMessage):
        """Perform the task described in the instruction."""
        command = instruction.message
        log_action(self.agent_id, f"Task executed: {command}")

        # Create a DataMessage for the result
        result = DataMessage(
            message=f"Result of task '{command}' completed by {self.agent_id}",
            timestamp=int(time.time()),
            sender=str(self.agent_id),
        )

        # Use the router to publish the result
        await self.publish_message(result, topic_id=DefaultTopicId())

    @event
    async def handle_data(self, message: DataMessage, ctx: MessageContext) -> None:
        """Handle incoming data from other sources."""
        log_action(self.agent_id, f"Data received: {message}")