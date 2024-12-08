import logging
import time
from typing import List, Dict, Any, Optional

from agents.agent_base import AgentSecBaseAgent
from autogen_core.components import rpc, event
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import sign_message
from messages.messages import DataMessage, AuthUserMessage, InstructionMessage
from autogen_core.components.models import ChatCompletionClient, SystemMessage, UserMessage

from utils.fetch import DataManager
from utils.context import parse_context

from data.db_manager import write_data
from security.log_chain import log_action

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CoreAgent(AgentSecBaseAgent):
    """Core Agent responsible for processing user commands and routing data."""

    def __init__(self, 
                agent_id: str, 
                model_client: ChatCompletionClient, 
                description: str = "Core Agent managing tasks and authorizations.",
                agent_name: str = "core_agent"):
        super().__init__(description=description)
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.model_client = model_client
        self._system_messages = [
            SystemMessage(
                "You are the highest authorized agent of a secure multi-agent system. Your role is to evaluate all data and formulate sanitized instructions to lower clearance agents."
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
    async def handle_instruction(self, message: AuthUserMessage, ctx: MessageContext) -> None:
        """
        Handle incoming instructions from the authorized end user.
        This method:
        - Logs the instruction.
        - Fetches & decrypts all data (clearance 3 for CoreAgent).
        - Sends user message + context to the model.
        - Signs and relays the resulting instruction to the auditor.
        """
        log_action(self.agent_id, f"Received instruction: {message}")
        logger.info(f"{self.agent_id}: Instruction received: {message}")

        # Fetch all data since CoreAgent has highest clearance (3)
        decrypted_context = self.data_manager.fetch_data_by_clearance_level(3)
        # Add context to message
        contextualized_message = message.message + parse_context(decrypted_context)
        # Prepare the user message
        user_message = UserMessage(content=contextualized_message, source="user")
        
        # Build the final messages for the model
        final_messages = self._system_messages + [user_message]

        # Send to model client
        response = await self.model_client.create(final_messages, cancellation_token=ctx.cancellation_token)
        logger.info(f"{self.agent_id}: Model client responded with: {response.content}")

        # Create and sign the instruction message
        instruction_message = self._create_instruction_message(response.content, message.token)
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
        Handle incoming data from Edge Agents:
        - Prompt for classification
        - Assign clearance level
        - Write to DB
        - Forward to the auditor
        """
        log_action(self.agent_id, f"Data received: {message}")
        logger.info(f"{self.agent_id}: Data received: {message}")

        clearance_level = self._prompt_for_clearance(message)
        if clearance_level is None:
            logger.warning(f"{self.agent_id}: Invalid clearance level. Classification aborted.")
            return None

        message.clearance_level = clearance_level
        log_action(self.agent_id, f"Data assigned clearance level {clearance_level}")
        logger.info(f"{self.agent_id}: Data assigned clearance level {clearance_level}.")

        write_data(message.model_dump())
        logger.debug(f"{self.agent_id}: Data updated in the database.")

        recipient = AgentId(type="auditor_agent", key="default")
        await self.send_message(message, recipient)
        log_action(self.agent_id, f"Data relayed to {recipient}.")
        logger.info(f"{self.agent_id}: Data relayed to {recipient}.")
        return message

    def _prompt_for_clearance(self, message: DataMessage) -> Optional[int]:
        """
        Prompts the user to classify the data's clearance level.
        In a non-interactive environment, this would be replaced by a pre-defined logic or configuration.
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