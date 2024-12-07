import logging
import copy
from agents.agent_base import AgentSecBaseAgent
from autogen_core.components import rpc, event
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import sign_message
from data.db_manager import read_all_data, write_data
from security.encryption_tools import decrypt_data
from security.log_chain import log_action
from messages.messages import DataMessage, AuthUserMessage, InstructionMessage
from autogen_core.components.models import ChatCompletionClient, SystemMessage, UserMessage
import time

class CoreAgent(AgentSecBaseAgent):
    """Core Agent responsible for processing user commands and routing data."""

    def __init__(self, agent_id: str, model_client: ChatCompletionClient, description: str = "Core Agent managing tasks and authorizations."):
        """
        Initialize the CoreAgent with an agent ID and description.

        Args:
            agent_id (str): Unique identifier for the agent.
            description (str): Description of the agent's purpose.
        """
        super().__init__(description=description)
        self._system_messages = [SystemMessage("You are a the highest authorized agent of a secure multi-agent system. Your role is to evaluate all data and formulate data-sanitized instructions to lower clearance agents.")]
        self.agent_id = agent_id
        self.model_client = model_client
        logging.info(f"CoreAgent initialized with ID: {self.agent_id}")

    async def on_start(self):
        """Perform setup tasks when the agent starts."""
        print(f"{self.agent_id}: Starting and loading data.")
        # Temporary setup for example purposes
        decrypted_data = await self.fetch_and_decrypt_all_data()
        print(f"{self.agent_id}: Decrypted data loaded for processing: {decrypted_data}")

    def fetch_and_decrypt_all_data(self):
        """
        Fetch all data from the database and temporarily decrypt it for processing.

        Returns:
            List[dict]: A list of decrypted data items.
        """
        try:
            all_data = read_all_data()
            decrypted_data = []
            for item in all_data:
                if item["clearance_level"] > 0:
                    try:
                        item["content"] = decrypt_data(item["content"], self.agent_id)
                        log_action(self.agent_id, f"Decrypted data item {item['id']}.")
                    except Exception as e:
                        log_action(self.agent_id, f"Failed to decrypt data item {item['id']}: {e}")
                        continue
                decrypted_data.append(item)
            return decrypted_data
        except Exception as e:
            log_action(self.agent_id, f"Error fetching data: {e}")
            return []

    @rpc
    async def handle_instruction(self, message: AuthUserMessage, ctx: MessageContext) -> None:
        """
        Handle incoming instructions from the authorized end user.

        Args:
            message (AuthUserMessage): The original user instruction message received, with an auth token.
            ctx (MessageContext): The context of the message.
        """
        log_action(self.agent_id, f"Received instruction: {message}")
        print(f"{self.agent_id}: Instruction received: {message}")

        # Create a UserMessage for the model client
        user_message = UserMessage(content=message.message, source="user")
        # Send the message to the model client and await a response
        response = await self.model_client.create(
            self._system_messages + [user_message],
            cancellation_token=ctx.cancellation_token
        )
        
        print(f"{self.agent_id}: Model client responded with: {response.content}")

        # Create a new InstructionMessage with the response content
        instruction_message = InstructionMessage(
            message=response.content,
            sender=str(self.agent_id),
            timestamp=int(time.time()),
            token=message.token,
            signature=''
        )

        # Sign the new instruction message
        signed_instruction = sign_message(instruction_message)

        # Log the signing event
        log_action(self.agent_id, f"Signed instruction: {signed_instruction}")
        print(f"{self.agent_id}: Instruction signed and logged.")

        # Relay the signed instruction to the AuditorAgent
        recipient = AgentId(type="auditor_agent", key="default")
        await self.send_message(signed_instruction, recipient)
        log_action(self.agent_id, f"Instruction relayed to {recipient}.")
        print(f"{self.agent_id}: Instruction relayed to {recipient}.")
    
    @event
    async def handle_data(self, message: DataMessage, ctx: MessageContext) -> DataMessage:
        """
        Handle incoming data from Edge Agents and classify it based on clearance level.

        Args:
            message (DataMessage): The data message received.
            ctx (MessageContext): The context of the message.
        """
        log_action(self.agent_id, f"Data received: {message}")
        print(f"{self.agent_id}: Data received: {message}")

        # Prompt the user to assign a clearance level to the data
        print(f"Classify the clearance level of this data (1-3): {message.content}")
        try:
            clearance_level = int(input("Enter clearance level (1-3): "))
            if clearance_level < 1 or clearance_level > 3:
                raise ValueError("Invalid clearance level.")
        except ValueError as e:
            log_action(self.agent_id, f"Data classification failed: {e}")
            print(f"{self.agent_id}: Invalid clearance level entered.")
            return

        # Assign clearance level
        message.clearance_level = clearance_level
        log_action(self.agent_id, f"Data assigned clearance level {clearance_level}")
        print(f"{self.agent_id}: Data assigned clearance level {clearance_level}.")

        # Update the database
        write_data(message.model_dump())
        print(f"{self.agent_id}: Data updated in the database.")

        # Relay the classified data to the AuditorAgent
        recipient = AgentId(type="auditor_agent", key="default")
        await self.send_message(message, recipient)
        log_action(self.agent_id, f"Data relayed to {recipient}.")
        print(f"{self.agent_id}: Data relayed to {recipient}.")