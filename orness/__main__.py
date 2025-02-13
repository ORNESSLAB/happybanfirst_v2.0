import logging
import logging.config
import pprint
import argparse
import orness.utils as utils
from dotenv import  set_key, dotenv_values, load_dotenv
import os
import importlib
import yaml
import configparser



def modify_logfile(new_filename):
    """Modifie le nom du fichier de log dans logging.yaml."""
    log_file = os.getenv("LOG_CONF_FILE")
    with open(log_file, "r") as f:
        try:
            config = yaml.load(f, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)
    # Recherche du gestionnaire de fichier et modification du nom du fichier
    for handler in config["handlers"].values():
        if handler["class"] == "logging.FileHandler":
            handler["filename"] = new_filename
            break

    with open(log_file, "w") as f:
        yaml.dump(config, f)

def setup_logging(default_path=os.getenv("LOG_CONF_FILE"), default_level=logging.INFO):
    """Setup logging configuration."""
    print(default_path)
    if os.path.exists(default_path):
        with open(default_path, 'rt') as f:
            config = yaml.safe_load(f.read())
            print(config)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        print(f"default path not found {default_path}")

def modify_env(key, value):
    variables = dotenv_values('.env')
    variables[key] = value
    for k, v in variables.items():
        set_key('.env', k, v)
    
def input_credentials():
    try:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        modify_env('IB_USERNAME', username)
        modify_env('IB_PASSWORD', password)
    except Exception as e:
        raise

def input_host():
    try:
        host = input("Enter your host: ")
        modify_env('IB_HOST', host)
    except Exception as e:
        raise
    

logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    parse = argparse.ArgumentParser(prog='orness api', description='Orness api is the API client of Ibanfirst', epilog='Text at the bottom of help')
    parse.add_argument('-v','--verbose', help='Verbose mode change log level', action='store_true')
    parse.add_argument('--set-credentials', help='Set credentials', action='store_true')
    parse.add_argument('--log-file', help='Change log file', type=str)
    parse.add_argument('--wallet', choices = ['list', 'create', 'id'], help='Create a new wallet or list wallets', type=str, default='list')
    parse.add_argument('--external-bank-account', choices=['list', 'create', 'id'], help='About external bank account', type=str)
    parse.add_argument('--payment', choices=['list', 'submit', 'id', 'status'], help='Submit payment', type=str, default='list')
    parse.add_argument('-f','--file', help='Excel,csv or json file ', type=str)
    parse.add_argument('--env', help='select environment', choices=['DEV', 'PROD'], default='DEV', metavar='ENV', type=str)
    parse.add_argument('-o', '--opt', help='option to filter the list of the wallet or payment', type=str)
    parse.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    parse.add_argument('--set-host', help='Change host', type=str)
    
    
    log_file = os.getenv('LOG_FILE')
    args = parse.parse_args()
    
    #LOG
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    #file_handler = logging.FileHandler(log_file)
    
    #file_handler.setFormatter(formatter)
    #logger.addHandler(file_handler)
    logger.addHandler(logging.StreamHandler())

    logger.info("Orness api started")
    
    if args.log_file:
        log_file = input("Enter  the name of the file in which you will save your logs: ")
        logger.info("Change log file to {}".format(log_file))
        modify_env('LOG_FILE', log_file)
    if args.set_credentials:
        try:
            input_credentials()
            logger.info("Credentials set for {}".format(username))
        except Exception as e:
            logger.error(pprint.pprint(e))

    if args.set_host:
        try:
            input_host()
            logger.info("Host set to {host}")
        except Exception as e:
            logger.error(pprint.pprint(e))

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    if args.wallet:
        if args.wallet == 'list':
            utils.get_wallets()
        if args.wallet == 'create':
            utils.create_wallets(args.file)
        if args.wallet == 'id':
            utils.get_wallet_id(args.opt)
        
    if args.external_bank_account:
        if args.external_bank_account == 'list':
            utils.get_external_bank_accounts()
        if args.external_bank_account == 'create':
            utils.create_external_bank_account(args.file)
        if args.external_bank_account == 'id':
            utils.get_external_bank_account(args.opt)
    if args.payment:
        if args.payment == 'id':
            utils.get_payment_by_id(args.opt)
        if args.payment == 'submit':
            utils.post_payment(args.file) 
        if args.payment == 'status':
            utils.get_payments_status(args.opt)

        

    

    
if __name__ == "__main__":
    main()
    
    