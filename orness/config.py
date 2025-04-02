import os
import logging
from ibanfirst_client import Configuration as Conf
from dotenv import load_dotenv



logger = logging.getLogger(__name__)


class Config(Conf):
    """
    Configuration class for the iBanFirst API client."""
    def __init__(self):
    
        """
        Constructor for the class. It sets the variables from the environment variables.
        
        """
        super().__init__()
        
        
    

          
