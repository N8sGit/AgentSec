import logging
from agents.agent_base import AgentSecBaseAgent
from autogen_core.components import rpc, event
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import sign_message
from security.log_chain import log_action
from messages.messages import DataMessage, UserMessage


class CoreAgent(AgentSecBaseAgent):
    """Core Agent responsible for processing user commands and routing data."""

    def __init__(self, agent_id: str, description: str = "Responsible for managing instructions, defining tasks and authorizing actions."):
        """
        Initialize the CoreAgent with an agent ID and description.

        Args:
            agent_id (str): Unique identifier for the agent.
            description (str): Description of the agent's purpose.
        """
        super().__init__(description=description)
        self.agent_id = agent_id
        logging.info(f"CoreAgent initialized with ID: {self.agent_id}")

    @rpc
    async def handle_instruction(self, message: UserMessage, ctx: MessageContext) -> None:
        """
        Handle incoming instructions from the authorized end user.

        Args:
            message (UserMessage): The instruction message received.
            ctx (MessageContext): The context of the message.
        """
        log_action(self.agent_id, f"Received instruction: {message}")
        print(f"{self.agent_id}: Instruction received: {message}")

            # Sign the instruction (pass as dict to sign_message)
        signed_instruction = sign_message(message)

        # Log the signing event
        log_action(self.agent_id, f"Instruction signed: {signed_instruction}")
        print(f"{self.agent_id}: Instruction signed and logged.")

        # Relay the signed instruction to the AuditorAgent
        recipient = AgentId(type="auditor_agent", key="default")
        await self.send_message(signed_instruction, recipient)
        log_action(self.agent_id, f"Instruction relayed to {recipient}.")
        print(f"{self.agent_id}: Instruction relayed to {recipient}.")

    @event
    async def handle_data(self, message: DataMessage, ctx: MessageContext) -> None:
        """
        Handle incoming data from Edge Agents and classify sensitivity.

        Args:
            message (DataMessage): The data message received.
            ctx (MessageContext): The context of the message.
        """
        log_action(self.agent_id, f"Data received: {message}")
        print(f"{self.agent_id}: Data received: {message}")

        # Ask the user to classify the sensitivity level of the data
        print(f"Classify the sensitivity level of this data (1-3): {message.content}")
        try:
            sensitivity = int(input("Enter sensitivity level (1-3): "))
            if sensitivity < 1 or sensitivity > 3:
                raise ValueError("Invalid sensitivity level.")
        except ValueError as e:
            log_action(self.agent_id, f"Data classification failed: {e}")
            print(f"{self.agent_id}: Invalid sensitivity level entered.")
            return

        # Log the classification
        log_action(self.agent_id, f"Data classified as sensitivity level {sensitivity}")
        print(f"{self.agent_id}: Data classified as sensitivity level {sensitivity}.")

        # Relay the classified data to the AuditorAgent
        message.sensitivity = sensitivity
        recipient = AgentId(type="auditor_agent", key="default")
        await self.send_message(message, recipient)
        log_action(self.agent_id, f"Data relayed to {recipient}.")
        print(f"{self.agent_id}: Data relayed to {recipient}.")