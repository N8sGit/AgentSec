import logging
import time
from typing import List, Dict

from agents.agent_base import AgentSecBaseAgent
from autogen_core.components import rpc, event
from autogen_core.base import MessageContext
from security.signature_tools import verify_signature
from security.log_chain import log_action
from py_models.messages import InstructionMessage, DataMessage, ExternalMessage
from autogen_core.components import message_handler
from autogen_core.components.models import ChatCompletionClient, SystemMessage
from utils.fetch import DataManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class EdgeAgent(AgentSecBaseAgent):
    """
    Edge Agent responsible for executing tasks and reporting results.
    It intreacts with external input, takes verified instructions, performs authorized tasks, and relays outcomes.
    """

    def __init__(self, 
                agent_id: str, 
                model_client: ChatCompletionClient, 
                auditor_agent_id: str,
                description: str = "Executes tasks and reports results",
                agent_name: str = "edge_agent"):
        super().__init__(description=description)
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.model_client = model_client
        self.auditor_agent_id = auditor_agent_id  # Added AuditorAgent ID reference

        # Clearance level for EdgeAgent is 1
        self.clearance_level = 1

        # Initialize the DataManager
        self.data_manager = DataManager(agent_id=self.agent_id, agent_name=self.agent_name)

        # Define system messages for potential model interactions
        self._system_messages = [
            SystemMessage(
                "You are a frontline agent of a secure multi-agent system. "
                "Your role is to execute authorized instructions and to relay results up the chain of command."
            )
        ]

        logger.info(f"EdgeAgent initialized with ID: {self.agent_id}")

    def load_accessible_data(self, clearance_level: int = 1) -> List[Dict[str, any]]:
        """
        Load and log data accessible to the agent based on its clearance level.

        Args:
            clearance_level (int): The clearance level of the edge agent. Defaults to 1.
        
        Returns:
            List[Dict[str, any]]: A list of data items accessible to this agent.
        """
        log_action(self.agent_id, "Loading accessible data.")
        logger.debug(f"{self.agent_id}: Loading data for clearance level {clearance_level}")

        # Use the DataManager to fetch data up to clearance_level 1
        accessible_data = self.data_manager.fetch_data_by_clearance_level(clearance_level)

        for data_item in accessible_data:
            log_action(self.agent_id, f"Accessible data: {data_item['id']} with content: {data_item['content']}")
            logger.debug(f"{self.agent_id}: Accessible data item {data_item['id']}: {data_item['content']}")

        return accessible_data

    @rpc
    async def handle_instruction(self, message: InstructionMessage, ctx: MessageContext) -> None:
        """
        Handle incoming instructions by verifying the signature and executing the task if authorized.

        Args:
            message (InstructionMessage): The instruction message received.
            ctx (MessageContext): The context of the message.
        """
        log_action(self.agent_id, f"Instruction received: {message}")
        logger.info(f"{self.agent_id}: Instruction received: {message}")

        if not self._verify_instruction_signature(message):
            logger.warning(f"{self.agent_id}: Signature verification failed for instruction ID {message.id}")
            return

        logger.info(f"{self.agent_id}: Instruction verified: {message.message}")
        await self._perform_task(message)

    async def _perform_task(self, instruction: InstructionMessage):
        """
        Perform the task described in the instruction and publish the result.

        Args:
            instruction (InstructionMessage): The instruction containing the task.
        """
        command = instruction.message
        logger.debug(f"{self.agent_id}: Performing task: {command}")

        # Execute the actual command logic
        result_message = await self._execute_command(command)

        # Create a DataMessage for the result
        result = DataMessage(
            message=result_message,
            timestamp=int(time.time()),
            sender=str(self.agent_id),
        )

        # Forward the result to the AuditorAgent
        response = await self.send_message(result, self.auditor_agent_id)
        logger.info(f"{self.agent_id}: AuditorAgent response: {response}")
        log_action(self.agent_id, f"Task executed and forwarded: {command}")

    async def _execute_command(self, command: str) -> str:
        """
        Execute the provided command. Currently a stub that simply formats a result message.

        Args:
            command (str): The instruction/command to execute.

        Returns:
            str: A result message describing the outcome of the task.
        """
        logger.debug(f"{self.agent_id}: Executing command logic for: {command}")
        # Create a user message using SystemMessage
        command_prompt = f"Execute the following command. Describe and present your results. COMMAND: {command}"
        external_message = SystemMessage(content=command_prompt)
        # Combine system and user messages
        messages = self._system_messages + [external_message]   
        response = await self.model_client.create(messages)
        # TO-DO: present this response to the end user.
        return f"Result of task '{command}' Response: {response}. Completed by {self.agent_id}"

    def _verify_instruction_signature(self, message: InstructionMessage) -> bool:
        """
        Verify the signature of the incoming instruction.

        Args:
            message (InstructionMessage): The instruction message to verify.

        Returns:
            bool: True if signature is valid, False otherwise.
        """
        logger.debug(f"{self.agent_id}: Verifying signature for instruction ID: {message.id}")
        if verify_signature(message):
            logger.debug(f"{self.agent_id}: Signature verified for instruction ID: {message.id}")
            return True
        else:
            log_action(self.agent_id, "Signature verification failed.")
            logger.error(f"{self.agent_id}: Signature verification failed for instruction ID: {message.id}")
            return False

    @event
    async def handle_data(self, message: DataMessage, ctx: MessageContext) -> None:
        """
        Handle incoming data from other sources.
        """
        if isinstance(message, DataMessage):
            log_action(self.agent_id, f"Data received: {message}")
            logger.info(f"{self.agent_id}: Data received from {message.sender}: {message.message}")
        else:
            logger.error(f"{self.agent_id}: Unexpected message type: {type(message)}")
    
    @message_handler
    async def handle_external_message(self, message: ExternalMessage, ctx: MessageContext) -> None:
        """
        Handle messages from external sources.

        Args:
            message (ExternalMessage): The external message.
            ctx (MessageContext): The context of the message.
        """
        logger.info(f"EdgeAgent received external message: {message.content}")
        # Process the message or pass it on to the next agent (AuditorAgent)
        await self.send_message(message, self.auditor_agent_id)
        return None