import asyncio
import threading
import queue
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId
from agents.core_agent import CoreAgent
from agents.auditor_agent import AuditorAgent
from agents.edge_agents.edge_agent_one import EdgeAgent
from security.authenticate_user import authenticate_user, generate_token
from py_models.messages import ExternalMessage  # Use ExternalMessage
from autogen_ext.models import OpenAIChatCompletionClient

# Queues for external environment communication
incoming_external_messages = queue.Queue()
outgoing_agent_messages = queue.Queue()

async def main():
    # Authenticate the user
    clearance_level = authenticate_user()
    if clearance_level is None:
        print("Exiting due to failed authentication.")
        return
    user_id = "n"
    user_token = generate_token(clearance_level)

    # Initialize runtime and agent IDs
    runtime = SingleThreadedAgentRuntime()
    core_agent_id = AgentId("core_agent", "default")
    auditor_agent_id = AgentId("auditor_agent", "default")
    edge_agent_id = AgentId("edge_agent_one", "default")

    # Initialize model client
    openai_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    # Register agents
    await CoreAgent.register(
        runtime,
        "core_agent",
        lambda: CoreAgent(
            agent_id=core_agent_id,
            model_client=openai_client,
            signing_token=user_token
        ),
    )

    await AuditorAgent.register(
        runtime,
        "auditor_agent",
        lambda: AuditorAgent(
            model_client=openai_client,
            agent_id=auditor_agent_id,
            core_agent_id=core_agent_id,
            edge_agent_id=edge_agent_id
        ),
    )

    await EdgeAgent.register(
        runtime,
        "edge_agent_one",
        lambda: EdgeAgent(
            model_client=openai_client,
            agent_id=edge_agent_id,
            auditor_agent_id=auditor_agent_id,
            outgoing_queue=outgoing_agent_messages
        ),
    )

    runtime.start()

    # Start Flask webserver in a separate thread
    from webserver import start_flask_app
    flask_thread = threading.Thread(
        target=start_flask_app,
        args=(incoming_external_messages, outgoing_agent_messages),
        daemon=True
    )
    flask_thread.start()

# Main loop
    while True:
        # Handle external environment input
        try:
            external_msg_content = incoming_external_messages.get_nowait()
        except queue.Empty:
            external_msg_content = None

        if external_msg_content:
            # Create an ExternalMessage and send it to the EdgeAgent
            external_message = ExternalMessage(
                content=external_msg_content,
                sender="unknown_source",
            )
            response_message = await runtime.send_message(
                message=external_message,
                recipient=edge_agent_id
            )
            # Place the response into the outgoing queue for the Flask server
            outgoing_agent_messages.put(response_message)

        await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(main())