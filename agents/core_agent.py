# agents/core_agent.py

from agents.agent_base import AgentBase
from security.encryption_tools import encrypt_data, decrypt_data
from security.permissions import get_clearance_level
from agents.auditor_agent import AuditorAgent
from security.blockchain import log_action
from autogen import Agent, Message

class CoreAgent(Agent):
    def __init__(self, name='CoreAgent'):
        super().__init__(name)
        self.clearance_level = get_clearance_level(self.name)
        self.auditor_agent = None  # Will be set during initialization

    def set_auditor(self, auditor_agent):
        self.auditor_agent = auditor_agent

    def handle_message(self, message):
        # Core Agent processes messages if needed
        pass

    def process_command(self, command, user_token):
        if not self.authenticate(user_token):
            print("Authentication failed.")
            return
        if self.is_sensitive_command(command):
            if not self.get_user_approval(command):
                print("User did not approve the sensitive action.")
                return

        # Encrypt command based on clearance level
        encrypted_command = encrypt_data(command, self.clearance_level)

        # Log the action
        print('action logged')
        #log_action(self.name, 'Issued command.')

        # Auditor verifies the action
        msg = Message(
            sender=self.name,
            receiver=self.auditor_agent.name,
            content=encrypted_command
        )
        self.send_message(msg)