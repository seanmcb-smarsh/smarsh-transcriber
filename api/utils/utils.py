import yaml

def read_config(yaml_file):
    with open(yaml_file, 'r') as configs:
        settings = yaml.load(configs, Loader=yaml.FullLoader)

        return settings