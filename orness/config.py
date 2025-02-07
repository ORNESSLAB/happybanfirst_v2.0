import os
import logging
import pprint
from dotenv import load_dotenv
from ibanfirst_client import Configuration as Conf
from orness.header_generator import IBanFirst



# Environment variables are from .env
load_dotenv()

class Log:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s-%(levelname)s:%(message)s', level=logging.DEBUG, filename="orness_api.log")
    def get_logger(self):
        return self.logger
    def display_format_data(self, data:list) -> str:
        return pprint.pformat(data)
    
    def display_format_http_error(self, error) -> str:
        return pprint.pformat(error)



class Config(Conf):
    """
    Configuration class for the iBanFirst API client."""
    def __init__(self):
    
        """
        Constructor for the class. It sets the variables from the environment variables.
        
        """
        super().__init__()
        self.host = os.getenv('IB_HOST')
        print(f"Connected on: {self.host}") 
              
    def get_header(self):
        """
        Retrieve the authentication header for iBanFirst API requests.

        This method generates a WSSE header using the username and password
        stored in environment variables. The header is used to authenticate
        requests to the iBanFirst API.

        :return: A dictionary containing the WSSE header.
        """
        header = IBanFirst(user_id=os.getenv('IB_USERNAME'), password=os.getenv('IB_PASSWORD')).generate_header()
        header['User-Agent'] = "Orness/1.0.0/python"
        return header
        #return IBanFirst(user_id=self.username, password=self.password).generate_header()



if __name__ == '__main__':
    cf = Config()
    df = Config()
    print("success" if id(cf.get_header()) == id(df.get_header()) else "non")

    print(cf.get_header())

          
