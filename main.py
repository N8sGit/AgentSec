import asyncio
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId
from agents.core_agent import CoreAgent
from agents.auditor_agent import AuditorAgent
from agents.edge_agents.edge_agent_one import EdgeAgent
from security.authenticate_user import authenticate_user, generate_token
from messages.messages import UserMessage


async def main():
    # Authenticate the user
    clearance_level = authenticate_user()
    if clearance_level is None:
        print("Exiting due to failed authentication.")
        return

    # Generate a token for the authenticated user
    user_id = "n"
    user_token = generate_token(clearance_level)

    # Initialize the runtime
    runtime = SingleThreadedAgentRuntime()

    # Create AgentIds
    core_agent_id = AgentId("core_agent", "default")
    auditor_agent_id = AgentId("auditor_agent", "default")
    edge_agent_one_id = AgentId("edge_agent_one", "default")

    # Register agents with the runtime
    await CoreAgent.register(
        runtime,
        "core_agent",
        lambda: CoreAgent(
            agent_id=core_agent_id
        )
    )

    await AuditorAgent.register(
        runtime,
        "auditor_agent",
        lambda: AuditorAgent(
            agent_id=auditor_agent_id
        )
    )

    await EdgeAgent.register(
        runtime,
        "edge_agent_one",
        lambda: EdgeAgent(
            agent_id=edge_agent_one_id
        )
    )

    # Start the runtime
    runtime.start()

    # Use asynchronous input to prevent blocking the event loop
    user_command = await asyncio.to_thread(input, "Enter your command: ")

    # Wrap the user command in the appropriate message type
    message = UserMessage(
        message=user_command,
        sender=user_id,
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