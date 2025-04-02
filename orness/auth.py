#Authentication Module
from orness.header_generator import IBanFirst as IB




class Authentication:
    """Authentication class for handling user authentication.
    
    This class is initialized with a username and password, and provides a method to generate an authentication header.
    
    Attributes:
        username (str): The username for authentication.
        password (str): The password for authentication.
    
    Methods:
        header(): Generates an authentication header using the provided username and password.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def header(self):
        """Generates the header for the user.
        
        This method creates a header using the user's credentials (username and password) 
        by instantiating the IB class and calling its `generate_header` method.
        
        Returns:
            str: The generated header.
        """
        return IB(self.username, self.password).generate_header()