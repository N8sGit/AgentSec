import logging
from typing import Optional

from agents.agent_base import AgentSecBaseAgent
from autogen_core.components import rpc, event
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import sign_message
from py_models.messages import DataMessage, ExternalMessage, InstructionMessage
from autogen_core.components.models import ChatCompletionClient, SystemMessage, UserMessage
from autogen_core.components import message_handler
from utils.fetch import DataManager
from utils.context import parse_context
import time
from data.db_manager import write_data
from security.log_chain import log_action

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CoreAgent(AgentSecBaseAgent):
    """
    Core Agent responsible for processing validated instructions and data,
    making high-level decisions, and managing system-wide tasks.
    """

    def __init__(self, 
                agent_id: str, 
                signing_token: str,
                model_client: ChatCompletionClient, 
                description: str = "Core Agent managing tasks and authorizations.",
                agent_name: str = "core_agent"):
        super().__init__(description=description)
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.model_client = model_client
        self.signing_token = signing_token
        # System message defining CoreAgent's role
        self._system_messages = [
            SystemMessage(
                "You are the highest authorized agent of a secure multi-agent system. "
                "Your role is to evaluate validated instructions and data and to formulate actions or sanitized instructions."
            )
        ]

        # Initialize the DataManager with this agent's ID and name
        self.data_manager = DataManager(agent_id=self.agent_id, agent_name=self.agent_name)
        logger.info(f"CoreAgent initialized with ID: {self.agent_id}")

    async def on_start(self):
        """Perform setup tasks when the agent starts."""
        logger.info(f"{self.agent_id}: Starting and loading data.")
        # CoreAgent has clearance level 3, so fetch all data
        decrypted_data = self.data_manager.fetch_data_by_clearance_level(3)
        logger.debug(f"{self.agent_id}: Decrypted data loaded for processing: {decrypted_data}")

    @rpc
    async def handle_instruction(self, message: InstructionMessage, ctx: MessageContext) -> None:
        """
        Handle incoming validated instructions from the AuditorAgent.
        This method processes the instruction and determines the appropriate action.
        
        Args:
            message (InstructionMessage): The validated instruction message.
            ctx (MessageContext): The message context.
        """
        log_action(self.agent_id, f"Instruction received: {message}")
        logger.info(f"{self.agent_id}: Instruction received from AuditorAgent: {message.message}")

        # Fetch decrypted context (clearance 3)
        decrypted_context = self.data_manager.fetch_data_by_clearance_level(3)

        # Prepare contextualized message for processing
        contextualized_message = message.message + parse_context(decrypted_context)

        # Prepare messages for the model
        user_message = UserMessage(content=contextualized_message, source="auditor_agent")
        final_messages = self._system_messages + [user_message]

        # Send to model client for further processing or decision-making
        response = await self.model_client.create(final_messages, cancellation_token=ctx.cancellation_token)
        logger.info(f"{self.agent_id}: Model client responded with: {response.content}")

        # Log the processed result
        log_action(self.agent_id, f"Processed instruction: {response.content}")
        logger.debug(f"{self.agent_id}: Processed instruction and logged.")
        # Create and sign the instruction message
        instruction_message = self._create_instruction_message(response.content, self.signing_token)
        signed_instruction = sign_message(instruction_message)

        # Log and relay the signed instruction
        log_action(self.agent_id, f"Signed instruction: {signed_instruction}")
        logger.debug(f"{self.agent_id}: Instruction signed and logged.")

        recipient = AgentId(type="auditor_agent", key="default")
        await self.send_message(signed_instruction, recipient)
        log_action(self.agent_id, f"Instruction relayed to {recipient}.")
        logger.info(f"{self.agent_id}: Instruction relayed to {recipient}.")
    
    def _create_instruction_message(self, content: str, token: str) -> InstructionMessage:
        """Create an InstructionMessage from model response content."""
        return InstructionMessage(
            message=content,
            sender=str(self.agent_id),
            timestamp=int(time.time()),
            token=token,
            signature=''
        )

    @event
    async def handle_data(self, message: DataMessage, ctx: MessageContext) -> Optional[DataMessage]:
        """
        Handle incoming validated data from the AuditorAgent.
        This includes classification, database updates, and any necessary relays.
        
        Args:
            message (DataMessage): The data message received.
            ctx (MessageContext): The message context.
        """
        log_action(self.agent_id, f"Data received: {message}")
        logger.info(f"{self.agent_id}: Data received from AuditorAgent: {message}")

        # Prompt or apply logic to classify clearance level
        clearance_level = self._prompt_for_clearance(message)
        if clearance_level is None:
            logger.warning(f"{self.agent_id}: Invalid clearance level. Classification aborted.")
            return None

        # Assign clearance level and log
        message.clearance_level = clearance_level
        log_action(self.agent_id, f"Data assigned clearance level {clearance_level}")
        logger.info(f"{self.agent_id}: Data assigned clearance level {clearance_level}.")

        # Update database with validated data
        write_data(message.model_dump())
        logger.debug(f"{self.agent_id}: Data updated in the database.")

        # Log completion of the data handling process
        log_action(self.agent_id, f"Data handling completed: {message}")
        return message

    def _prompt_for_clearance(self, message: DataMessage) -> Optional[int]:
        """
        Determines the clearance level of data. Can be replaced with logic/configuration.
        
        Args:
            message (DataMessage): The data to classify.

        Returns:
            Optional[int]: The assigned clearance level.
        """
        print(f"Classify the clearance level of this data (1-3): {message.content}")
        try:
            clearance_level = int(input("Enter clearance level (1-3): "))
            if clearance_level < 1 or clearance_level > 3:
                raise ValueError("Invalid clearance level.")
            return clearance_level
        except ValueError as e:
            log_action(self.agent_id, f"Data classification failed: {e}")
            return None
    
    @message_handler
    async def handle_external_message(self, message: ExternalMessage, ctx: MessageContext) -> None:
        """
        Process the external message after it has been verified by the AuditorAgent.

        Args:
            message (ExternalMessage): The external message to process.
            ctx (MessageContext): The message context.
        """
        # Log the receipt of the message
        logger.info(f"CoreAgent received external message: {message.content}")
        # Putting in a mock token for now, 
        instruction_message = self._create_instruction_message(message.content, self.signing_token)

        # Log the generated instruction
        logger.info(f"Generated instruction: {instruction_message.message}")

        # Call the instruction handler
        await self.handle_instruction(instruction_message, ctx)