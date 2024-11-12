# main.py
import asyncio
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId
from agents.core_agent import CoreAgent
from agents.auditor_agent import AuditorAgent
from agents.edge_agents.edge_agent_one import EdgeAgent
from security.authentication import generate_token
from messages.messages import InstructionMessage

async def main():
    # Initialize the runtime
    runtime = SingleThreadedAgentRuntime()

    # Register agents with the runtime using consistent identifiers
    await CoreAgent.register(runtime, "core_agent", lambda: CoreAgent())
    await AuditorAgent.register(runtime, "auditor_agent", lambda: AuditorAgent())
    await EdgeAgent.register(runtime, "edge_agent_one", lambda: EdgeAgent("edge_agent_one"))

    # Start the runtime
    runtime.start()  # Start processing messages in the background

    # Simulate user authentication
    user_id = 'user123'
    core_clearance_level = 3
    user_token = generate_token(user_id, core_clearance_level)

    # Use asynchronous input to prevent blocking the event loop
    user_command = await asyncio.to_thread(input, "Enter your command: ")

    # Create an AgentId for the core agent and send the message
    core_agent_id = AgentId("core_agent", "default")
    
    # Wrap the user command in the appropriate message type, including the token
    message = InstructionMessage(
        content=user_command,
        source=user_id,
        clearance_lvl=core_clearance_level,
        token=user_token
    )

    # Send the message to the core agent
    await runtime.send_message(message, core_agent_id)

    # Allow some time for agents to process messages
    await asyncio.sleep(1)

    # Stop the runtime after processing
    await runtime.stop()

if __name__ == '__main__':
    asyncio.run(main())