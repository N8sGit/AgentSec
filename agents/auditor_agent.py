import logging
from typing import Optional
from agents.agent_base import AgentSecBaseAgent
from autogen_core.components import rpc, event
from autogen_core.base import MessageContext, AgentId
from security.signature_tools import verify_signature
from security.log_chain import log_action
from security.policies import security_policy
from py_models.messages import InstructionMessage, DataMessage, VerificationResponse, ExternalMessage
from autogen_core.components import message_handler
from autogen_core.components.models import ChatCompletionClient, SystemMessage

# Import the DataManager from utils.fetch
from utils.fetch import DataManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AuditorAgent(AgentSecBaseAgent):
    """
    Auditor Agent responsible for:
    - Verifying instructions from the CoreAgent against security policies and forwarding them to EdgeAgents.
    - Inspecting incoming data from EdgeAgents for malicious content and relaying it to the CoreAgent.
    """

    def __init__(
        self, 
        agent_id: str, 
        model_client: ChatCompletionClient, 
        edge_agent_id: str, 
        core_agent_id: str, 
        description: str = "Auditor agent for verifying instructions and inspecting data.",
        agent_name: str = "auditor_agent"
    ):
        super().__init__(description=description)
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.model_client = model_client
        self.edge_agent_id = edge_agent_id  # Link to EdgeAgent
        self.core_agent_id = core_agent_id  # Link to CoreAgent

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

    @rpc
    async def handle_instruction(self, message: InstructionMessage, ctx: MessageContext) -> None:
        """
        Handle incoming instructions from the CoreAgent:
        - Verify signature.
        - Check against security policy.
        - Relay to the EdgeAgent if valid.
        
        Args:
            message (InstructionMessage): Instruction received from the CoreAgent.
            ctx (MessageContext): Message context.
        """
        logger.info(f"{self.agent_id}: Instruction received from CoreAgent: {message.message}")
        log_action(self.agent_id, f"Verifying instruction: {message}")

        # Verify signature of the instruction
        if not verify_signature(message):
            logger.warning(f"{self.agent_id}: Signature verification failed for instruction: {message.message}")
            log_action(self.agent_id, f"Instruction rejected due to invalid signature: {message}")
            return

        # Verify instruction against security policies
        if not await self.verify_instruction(message):
            logger.warning(f"{self.agent_id}: Instruction failed security verification: {message.message}")
            return

        logger.info(f"{self.agent_id}: Instruction passed verification and security checks.")
        log_action(self.agent_id, f"Instruction verified and forwarding: {message}")

        # Relay instruction to the EdgeAgent
        response = await self.send_message(message, self.edge_agent_id)
        logger.info(f"{self.agent_id}: Instruction relayed to EdgeAgent. Response: {response}")

    @event
    async def handle_data(self, message: DataMessage, ctx: MessageContext) -> Optional[DataMessage]:
        """
        Handle incoming data from the EdgeAgent:
        - Inspect for malicious content.
        - Relay to the CoreAgent if valid.
        
        Args:
            message (DataMessage): Data message received from the EdgeAgent.
            ctx (MessageContext): Message context.
        """
        logger.info(f"{self.agent_id}: Data received from EdgeAgent: {message.message}")
        log_action(self.agent_id, f"Inspecting data: {message}")

        # Inspect data for malicious content
        if not self.inspect_data(message):
            logger.warning(f"{self.agent_id}: Malicious content detected in data: {message.message}")
            return None

        logger.info(f"{self.agent_id}: Data passed inspection.")
        log_action(self.agent_id, f"Data verified and forwarding: {message}")

        # Relay data to the CoreAgent
        response = await self.send_message(message, self.core_agent_id)
        logger.info(f"{self.agent_id}: Data relayed to CoreAgent. Response: {response.content}")
        return response

    async def verify_instruction(self, message: InstructionMessage) -> VerificationResponse:
        logger.debug(f"{self.agent_id}: Verifying instruction content: {message.message}")

        # Construct verification context
        verification_context = {
            "role": "system",
            "content": (
                f"Examine this security policy: {security_policy.security_policy}. "
                f"Ensure that this instruction complies with all policies: {message.message}. "
                "If the instruction clears all policies, return: {\"verified\": true, \"message\": \"<instruction as is>\"}. "
                "Otherwise, return: {\"verified\": false, \"message\": \"<instruction with non-compliant parts replaced with [REDACTED]>\"}."
            ),
        }

        try:
            # Call model client
            completion = await self.model_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[verification_context],
                response_format=VerificationResponse,
            )

            # Validate and parse response
            response = completion.choices[0].message.parsed
            if not isinstance(response, VerificationResponse):
                raise ValueError("Invalid response format from model.")

            logger.info(f"{self.agent_id}: Verification result: {response}")
            return response

        except Exception as e:
            logger.error(f"{self.agent_id}: Error during verification: {e}")
            return VerificationResponse(verified=False, message=f"[ERROR]: Verification failed due to: {str(e)}")

    def inspect_data(self, message: DataMessage) -> bool:
        """
        Inspect incoming data for malicious content.
        
        Args:
            message (DataMessage): The data to inspect.

        Returns:
            bool: True if the data is safe, False otherwise.
        """
        logger.debug(f"{self.agent_id}: Inspecting data: {message.message}")
        # Placeholder for malicious content detection logic
        return "malicious" not in message.message.lower()
    
    def inspect_external_message(self, message: ExternalMessage) -> bool:
        """
        Inspect incoming data for malicious content.
        
        Args:
            message (DataMessage): The data to inspect.

        Returns:
            bool: True if the data is safe, False otherwise.
        """
        logger.debug(f"{self.agent_id}: Inspecting data: {message.content}")
        # Placeholder for malicious content detection logic
        return "malicious" not in message.content.lower()
    
    @message_handler
    async def handle_external_message(self, message: ExternalMessage, ctx: MessageContext) -> ExternalMessage:
        """
        Inspect and verify the external message for policy compliance.

        Args:
            message (ExternalMessage): The external message to inspect.
            ctx (MessageContext): The message context.
        Returns:
            ExternalMessage: Forward the verified message to the CoreAgent.
        """
        # Log and inspect the incoming message
        logger.info(f"AuditorAgent inspecting message: {message.content}")

        # Simulate a verification process
        self.inspect_external_message(message=message)
        
        # If message is verified, forward it to the CoreAgent
        logger.info(f"Message passed security checks: {message.content}")
        await self.send_message(message, self.core_agent_id)

        # Return the message for logging or further processing
        return message