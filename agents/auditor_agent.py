import logging

from agents.agent_base import AgentSecBaseAgent
from autogen_core.components import rpc, event
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import verify_signature
from security.log_chain import log_action
from messages.messages import InstructionMessage, DataMessage
from autogen_core.components.models import ChatCompletionClient, SystemMessage

# Import the DataManager from utils.fetch
from utils.fetch import DataManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AuditorAgent(AgentSecBaseAgent):
    """
    Auditor Agent responsible for verifying and relaying commands.
    Checks signatures of incoming instructions, applies a sensitivity filter,
    and forwards them to the appropriate agents. Also validates data
    feedback from edge agents and passes it upward if appropriate.
    """

    def __init__(
        self, 
        agent_id: str, 
        model_client: ChatCompletionClient, 
        description: str = "Responsible for auditing and relaying commands.",
        agent_name: str = "auditor_agent"
    ):
        super().__init__(description=description)
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.model_client = model_client

        # Clearance level for AuditorAgent is 2
        self.clearance_level = 2

        # Initialize the DataManager
        self.data_manager = DataManager(agent_id=self.agent_id, agent_name=self.agent_name)

        # System message defining the role of the AuditorAgent
        self._system_messages = [
            SystemMessage(
                "You are an auditor of a secure multi-agent system. Your task is to review instructions "
                "to ensure they contain no sensitive information and to also flag any suspicious activity."
            )
        ]

        logger.info(f"AuditorAgent initialized with ID: {self.agent_id}")

    def sensitivity_filter(self, message: InstructionMessage) -> InstructionMessage:
        """
        Filter sensitive content from instructions.
        Currently a stub that does no modification.
        
        Args:
            message (InstructionMessage): The instruction to filter.

        Returns:
            InstructionMessage: The filtered (or unchanged) instruction.
        """
        log_action(self.agent_id, f"Triggered sensitivity filter for instruction: {message.message}")
        logger.debug(f"{self.agent_id}: Applying sensitivity filter to instruction: {message.message}")
        # Stub: No modifications made currently
        return message

    def validate_feedback(self, message: DataMessage) -> bool:
        """
        Validate feedback to ensure it contains no unauthorized commands.
        Currently a stub that always returns True.
        
        Args:
            message (DataMessage): The feedback data to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        log_action(self.agent_id, f"Triggered feedback validation for data {message.id}")
        logger.debug(f"{self.agent_id}: Validating feedback data with ID: {message.id}")
        # Stub: Assume all feedback is valid for now.
        return True

    def load_data(self, agent_clearance: int = 2):
        """
        Load all accessible data based on the agent's clearance level.
        
        Args:
            agent_clearance (int): The clearance level of the auditor. Defaults to 2.
        
        Returns:
            list: A list of data items accessible to this agent.
        """
        log_action(self.agent_id, "Loading data based on clearance level.")
        logger.debug(f"{self.agent_id}: Loading data for clearance level {agent_clearance}")

        # Use the DataManager to fetch and decrypt data up to clearance_level 2
        accessible_data = self.data_manager.fetch_data_by_clearance_level(agent_clearance)
        
        logger.info(f"{self.agent_id}: Accessible data (clearance {agent_clearance}): {accessible_data}")
        return accessible_data

    @rpc
    async def handle_instruction(self, message: InstructionMessage, ctx: MessageContext) -> None:
        """
        Handle incoming instructions from CoreAgent, verifying signatures,
        filtering for sensitive content, and relaying to EdgeAgentOne if valid.
        
        Args:
            message (InstructionMessage): The instruction message received.
            ctx (MessageContext): The message context.
        """
        log_action(self.agent_id, f"Raw instruction received: {message}")
        logger.info(f"{self.agent_id}: Raw instruction received: {message}")

        if not self._verify_instruction_signature(message):
            logger.warning(f"{self.agent_id}: Signature verification failed for instruction: {message.id}")
            return

        # Apply sensitivity filter
        filtered_message = self.sensitivity_filter(message)

        # Relay to EdgeAgentOne
        await self._relay_instruction(filtered_message, AgentId(type="edge_agent_one", key="default"))

    @event
    async def handle_data(self, message: DataMessage, ctx: MessageContext) -> None:
        """
        Handle feedback from EdgeAgents, validating it and relaying to the CoreAgent if appropriate.
        
        Args:
            message (DataMessage): The data message received.
            ctx (MessageContext): The message context.
        """
        log_action(self.agent_id, f"Raw data received: {message}")
        logger.info(f"{self.agent_id}: Raw data received: {message}")

        if not self.validate_feedback(message):
            logger.warning(f"{self.agent_id}: Feedback rejected for data ID: {message.id}")
            log_action(self.agent_id, f"Feedback rejected: {message}")
            return

        # If feedback is valid, relay to the CoreAgent
        await self._relay_data(message, AgentId(type="core_agent", key="default"))

    def _verify_instruction_signature(self, message: InstructionMessage) -> bool:
        """
        Verify the signature of an incoming instruction.

        Args:
            message (InstructionMessage): The instruction whose signature needs verification.

        Returns:
            bool: True if signature is valid, False otherwise.
        """
        logger.debug(f"{self.agent_id}: Verifying signature for instruction ID: {message.id}")
        if verify_signature(message):
            logger.info(f"{self.agent_id}: Signature verification successful for instruction ID: {message.id}")
            return True
        else:
            log_action(self.agent_id, "Signature verification failed.")
            logger.error(f"{self.agent_id}: Signature verification failed for instruction ID: {message.id}")
            return False

    async def _relay_instruction(self, message: InstructionMessage, recipient: AgentId) -> None:
        """
        Relay the given instruction message to the specified recipient.

        Args:
            message (InstructionMessage): The instruction message to relay.
            recipient (AgentId): The recipient agent ID.
        """
        await self.send_message(message, recipient)
        log_action(self.agent_id, f"Instruction relayed to {recipient}.")
        logger.info(f"{self.agent_id}: Instruction (ID: {message.id}) relayed to {recipient}.")

    async def _relay_data(self, message: DataMessage, recipient: AgentId) -> None:
        """
        Relay the given data message to the specified recipient.

        Args:
            message (DataMessage): The data message to relay.
            recipient (AgentId): The recipient agent ID.
        """
        await self.send_message(message, recipient)
        log_action(self.agent_id, f"Data relayed to {recipient}.")
        logger.info(f"{self.agent_id}: Data (ID: {message.id}) relayed to {recipient}.")