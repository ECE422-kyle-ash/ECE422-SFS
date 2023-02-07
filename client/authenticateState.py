
from state import State

class AuthenticateState(State):

    def run(self, client):
        # do auth stuff
        return client
