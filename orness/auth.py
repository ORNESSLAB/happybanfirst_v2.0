#Authentication Module
from orness.header_generator import IBanFirst as IB


class Authentication:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def header(self):
        return IB(self.username, self.password).generate_header()