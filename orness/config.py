import os
import logging
import pprint
import configparser 
from dotenv import load_dotenv
from ibanfirst_client import Configuration as Conf
from orness.header_generator import IBanFirst

load_dotenv()
def get_config():
    config = configparser.ConfigParser()
    config.read(os.getenv('CONFIG_FILE'))
    
    return config

# Environment variables are from .env

logger = logging.getLogger(__name__)

class Config(Conf):
    """
    Configuration class for the iBanFirst API client."""
    def __init__(self):
    
        """
        Constructor for the class. It sets the variables from the environment variables.
        
        """
        #self.config = get_config()
        super().__init__()
        #self.host = self.config['DEFAULT']['host']
        self.host = os.getenv('IB_HOST')
        logger.info("Connected on: {} as {}".format(self.host, os.getenv('IB_USERNAME')))
              
    def get_header(self):
        """
        Retrieve the authentication header for iBanFirst API requests.

        This method generates a WSSE header using the username and password
        stored in environment variables. The header is used to authenticate
        requests to the iBanFirst API.

        :return: A dictionary containing the WSSE header.
        """
        header = IBanFirst(user_id=os.getenv('IB_USERNAME') , password=os.getenv('IB_PASSWORD')).generate_header()
        header['User-Agent'] = "Orness/1.0.0/python"
        return header
        #return IBanFirst(user_id=self.username, password=self.password).generate_header()



if __name__ == '__main__':
    cf = Config()
    pprint.pprint(cf.get_header())

    

          
