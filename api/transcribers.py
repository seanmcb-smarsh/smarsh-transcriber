import torch
import yaml

from deepscribe_inference.config import TranscribeConfig, HardwareConfig, InferenceConfig
from deepscribe_inference.load_model import load_model, load_decoder
from deepscribe_inference.transcribe import run_inference
from trellis import PredictiveModel

def transcriber_factory(yaml_file):
    with open(yaml_file, "r") as configs:
        settings = yaml.load(configs, Loader=yaml.FullLoader)
        comps = settings["transcriber"].split('.')
        clz = __import__(comps[0])
        for comp in comps[1:]:
            clz = getattr(clz, comp)
        return clz(settings)

class DeepscribeTranscriber(PredictiveModel):

    def __init__(self,settings):
        self.device = torch.device(settings["device"])
        self.model = load_model(
            model_path=settings['model_path'],
            precision=HardwareConfig.precision,
            device=self.device)
        self.decoder = load_decoder(
            decoder_cfg=InferenceConfig.decoder,
            labels=self.model.labels)

    def predict(self,input_path):
        return run_inference(
            input_path=input_path,
            model=self.model,
            decoder=self.decoder,
            cfg=self.cfg,
            device=self.device)

