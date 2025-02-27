import os
import logging
import pprint
import configparser 
from ibanfirst_client.rest import ApiException
from dotenv import load_dotenv
from ibanfirst_client import Configuration as Conf
from orness.header_generator import IBanFirst
import redis

rd = redis.Redis(host='localhost', port=6379, db=0)

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
        print(self.host)
        logger.debug("Connected on: {} as {}".format(self.host, os.getenv('IB_USERNAME')))
              
    def get_header(self):
        """
        Retrieve the authentication header for iBanFirst API requests.

        This method generates a WSSE header using the username and password
        stored in environment variables. The header is used to authenticate
        requests to the iBanFirst API.

        :return: A dictionary containing the WSSE header.
        """
        
        try:
            header = IBanFirst(user_id=os.getenv('IB_USERNAME') , password=os.getenv('IB_PASSWORD')).generate_header()
            #header = IBanFirst(user_id=rd.get('user_id').decode('utf-8') , password=rd.get('password').decode('utf-8')).generate_header()
            header['User-Agent'] = "Orness/1.0.0/python"
            return header
        except ApiException as e:
            logger.error(pprint.pprint(e.reason))
        #return IBanFirst(user_id=self.username, password=self.password).generate_header()



if __name__ == '__main__':
    cf = Config()
    pprint.pprint(cf.get_header())

    

          
