import logging
from agents.agent_base import AgentSecBaseAgent
from autogen_core.components import rpc, event
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import verify_signature
from security.log_chain import log_action
from messages.messages import InstructionMessage, DataMessage
from autogen_core.components.models import ChatCompletionClient, SystemMessage
from data.db_manager import filter_data_by_clearance_level


class AuditorAgent(AgentSecBaseAgent):
    """Auditor Agent responsible for verifying and relaying commands."""

    def __init__(self, agent_id: str, model_client: ChatCompletionClient, description: str = "Responsible for auditing and relaying commands."):
        super().__init__(description=description)
        self._system_messages = [SystemMessage("You are an auditor of a secure multi-agent system. Your task is to review instructions to ensure they contain no sensitive information and to also flag any suspicious activity.")]
        self.agent_id = agent_id
        self.model_client = model_client
        logging.info(f"AuditorAgent initialized with ID: {self.agent_id}")

    def sensitivity_filter(self, message: InstructionMessage) -> InstructionMessage:
        """Filter sensitive content from instructions (Stub)."""
        log_action(self.agent_id, f"Triggered sensitivity filter for instruction: {message.message}")
        # Stub: No changes to the message yet
        return message

    def validate_feedback(self, message: DataMessage) -> bool:
        """Validate feedback to ensure it contains no unauthorized commands (Stub)."""
        log_action(self.agent_id, f"Triggered feedback validation for data {message.id}")
        # Stub: Assume all feedback is valid for now
        return True

    def load_data(self):
        """Load all accessible data based on the agent's clearance level."""
        log_action(self.agent_id, "Loading data based on clearance level.")
        accessible_data = filter_data_by_clearance_level(agent_clearance=2)  # Assuming auditor clearance level is 2
        logging.info(f"Accessible data for {self.agent_id}: {accessible_data}")

    @rpc
    async def handle_instruction(self, message: InstructionMessage, ctx: MessageContext) -> None:
        """
        Handle incoming instructions from CoreAgent, filtering sensitive content.

        Args:
            message (InstructionMessage): The instruction message received.
            ctx (MessageContext): The context of the message.
        """
        log_action(self.agent_id, f"Raw instruction received: {message}")
        print(f"{self.agent_id}: Raw instruction received: {message}")

        # Verify the signature of the instruction
        if not verify_signature(message):
            log_action(self.agent_id, "Signature verification failed.")
            print(f"{self.agent_id}: Signature verification failed.")
            return

        filtered_message = self.sensitivity_filter(message)
        recipient = AgentId(type="edge_agent_one", key="default")
        await self.send_message(filtered_message, recipient)
        log_action(self.agent_id, f"Instruction relayed to {recipient}.")
        print(f"{self.agent_id}: Instruction relayed to {recipient}.")

    @event
    async def handle_data(self, message: DataMessage, ctx: MessageContext) -> None:
        """
        Handle feedback from EdgeAgents, ensuring it contains no unauthorized commands.

        Args:
            message (DataMessage): The data message received.
            ctx (MessageContext): The context of the message.
        """
        log_action(self.agent_id, f"Raw data received: {message}")
        print(f"{self.agent_id}: Raw data received: {message}")

        if not self.validate_feedback(message):
            log_action(self.agent_id, f"Feedback rejected: {message.id}")
            print(f"{self.agent_id}: Feedback rejected.")
            return

        upward_recipient = AgentId(type="core_agent", key="default")
        await self.send_message(message, upward_recipient)
        log_action(self.agent_id, f"Data relayed to {upward_recipient}.")
        print(f"{self.agent_id}: Data relayed to {upward_recipient}.")