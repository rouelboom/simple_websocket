import pathlib
import yaml

BASE_DIR = pathlib.Path(__file__).parent.parent
config_path = BASE_DIR / 'config' / 'server_config.yaml'

UPDATE_DATA_TIME = 5

def get_config(path):
    with open(path) as file:
        config = yaml.safe_load(file)
        return config


config = get_config(config_path)
