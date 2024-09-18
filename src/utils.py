import logging
import yaml

def setup_logging(level=logging.INFO):  # Accept level as an argument
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    
def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)