import yaml

from dataclasses import dataclass
from typing import Type, Union, TypeVar
from importlib import import_module
T = TypeVar('T')

@dataclass
class TranscriptionAPIConfig():
    '''
    transcriber: string defining type of transcription object
    config: Should be config object relevant to the chosen transcription object
    '''
    transcriber: str
    config: Type[T]

def override(object, config_dict):
    for key, value in config_dict.items():
        attr = getattr(object, key)
        if isinstance(value, dict):
            override(attr, value)
        else:
            setattr(object, key, value)

def read_config(yaml_file):
    with open(yaml_file, 'r') as configs:
        settings = yaml.load(configs, Loader=yaml.FullLoader)
        transcribe_config = getattr(import_module(settings['config_module']), settings['config_object'])
        override(transcribe_config, settings['config'])

        return TranscriptionAPIConfig(transcriber = settings['transcriber'], config = transcribe_config.inference)