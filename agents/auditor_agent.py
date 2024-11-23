import logging
from agents.agent_base import AgentSecBaseAgent
from autogen_core.components import rpc, event
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import verify_signature
from security.log_chain import log_action
from messages.messages import InstructionMessage, DataMessage


class AuditorAgent(AgentSecBaseAgent):
    """Auditor Agent responsible for verifying and relaying commands."""

    def __init__(self, agent_id: str, description: str = "Responsible for auditing and relaying commands."):
        """
        Initialize the AuditorAgent with an agent ID and description.

        Args:
            agent_id (str): Unique identifier for the agent.
            description (str): Description of the agent's purpose.
        """
        super().__init__(description=description)
        self.agent_id = agent_id
        logging.info(f"AuditorAgent initialized with ID: {self.agent_id}")

    @rpc
    async def handle_instruction(self, message: InstructionMessage, ctx: MessageContext) -> None:
        """
        Handle incoming instructions from CoreAgent.

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

        # Log successful verification
        log_action(self.agent_id, f"Instruction verified: {message}")
        print(f"{self.agent_id}: Instruction verified.")

        # Relay the instruction to the appropriate EdgeAgent
        recipient = AgentId(type="edge_agent_one", key="default")
        await self.send_message(message, recipient)
        log_action(self.agent_id, f"Instruction relayed to {recipient}.")
        print(f"{self.agent_id}: Instruction relayed to {recipient}.")

    @event
    async def handle_data(self, message: DataMessage, ctx: MessageContext) -> None:
        """
        Handle incoming data from Edge Agents.

        Args:
            message (DataMessage): The data message received.
            ctx (MessageContext): The context of the message.
        """
        log_action(self.agent_id, f"Raw data received: {message}")
        print(f"{self.agent_id}: Raw data received: {message}")

        # Validate data format
        if not message:
            log_action(self.agent_id, "Invalid data format received.")
            print(f"{self.agent_id}: Invalid data format.")
            return

        # Log data verification
        log_action(self.agent_id, f"Data verified: {message}")
        print(f"{self.agent_id}: Data verified.")

        # Relay the data upward (e.g., CoreAgent)
        upward_recipient = AgentId(type="core_agent", key="default")
        await self.send_message(message, upward_recipient)
        log_action(self.agent_id, f"Data relayed to {upward_recipient}.")
        print(f"{self.agent_id}: Data relayed to {upward_recipient}.")