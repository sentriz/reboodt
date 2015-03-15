import yaml
import os

def load_yaml(path_relative_to_reboodt):

    current_folder = os.path.dirname(__file__)
    provisional_path = os.path.join(current_folder, os.pardir)
    parent_folder = os.path.abspath(provisional_path)
    yaml_file = os.path.join(
        parent_folder, path_relative_to_reboodt)
        
    with open(yaml_file, "r") as file:
        yaml_contents = yaml.load(file)
        
    return yaml_contents
    
config = load_yaml("config.yml")
servers = config["servers"]
admins = config["admins"]