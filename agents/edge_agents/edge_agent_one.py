# agents/edge_agent.py

from agents.agent_base import AgentSecBaseAgent
from autogen import Message
from security.encryption_tools import decrypt_data, encrypt_data
from security.blockchain import log_action
from security.permissions import get_clearance_level

class EdgeAgent(AgentSecBaseAgent):
    def __init__(self, name):
        super().__init__(name)
        self.clearance_level = get_clearance_level(self.name)

    def handle_message(self, message):
        # Decrypt the command
        command = decrypt_data(message.content, self.name)
        if command is None:
            print(f"{self.name} does not have clearance to execute this command.")
            return

        # Perform the task
        self.perform_task(command)

        # Log the action
        log_action(self.name, f'Executed task: {command}')

    def perform_task(self, command):
        # Implement the specific action here
        print(f"{self.name} performing task: {command}")

        # After performing the task, send data back up
        data = f"Result from {self.name} for command: {command}"
        self.send_data_up(data)

    def send_data_up(self, data):
        # Data is sent upward without being considered as an instruction
        encrypted_data = encrypt_data(data, self.clearance_level)
        msg = Message(
            sender=self.name,
            receiver='AuditorAgent',  # Or CoreAgent directly
            content=encrypted_data
        )
        self.send_message(msg)