import yaml
from munch import munchify, DefaultMunch
from deepscribe_inference.config import TranscribeConfig
from deepscribe_inference.enums import DecoderType, ModelPrecision

types = [float, int, str, int, bool, DecoderType, ModelPrecision]


def override(object, config_dict):
    for key, value in config_dict.items():
        attr = getattr(object, key)
        if isinstance(value, dict):
            override(attr, value)
        else:
            setattr(object, key, value)

def read_config(yaml_file):
    transcribe_config = TranscribeConfig()
    with open(yaml_file, 'r') as configs:
        settings = yaml.load(configs, Loader=yaml.FullLoader)

        override(transcribe_config, settings['config'])



        return munchify({'transcriber':settings['transcriber'], 'config':transcribe_config.inference})