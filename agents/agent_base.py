from autogen import Agent
from security.authentication import authenticate_source

class AgentBase:
    def __init__(self, name):
        self.name = name
        self.agent = Agent()
    def authenticate(self, token):
        return authenticate_source(token)