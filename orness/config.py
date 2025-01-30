import os
from ibanfirst_client import Configuration as Conf
from dotenv import dotenv_values, load_dotenv
from orness.header_generator import IBanFirst

# Environment variables are from .env
load_dotenv()

#Singleton design patter
class Config(Conf):
    def __init__(self):
        super().__init__()
        #Retreive environment variables 
        self.username = os.getenv('IB_USERNAME')
        self.password = os.getenv('IB_PASSWORD')
        self.host = os.getenv('IB_HOST')
        print('Connected on: {}'.format(self.host)) 
    def get_header(self):
        return IBanFirst(user_id=self.username, password=self.password).generate_header()



if __name__ == '__main__':
    cf = Config()
    df = Config()
    print("success" if id(cf.get_header()) == id(df.get_header()) else "non")

    print(dir(cf))

          
