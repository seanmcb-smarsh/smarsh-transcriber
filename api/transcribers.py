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
        clz = globals()[comps[0]]
        for comp in comps[1:]:
            clz = getattr(clz, comp)
        return clz(settings)

class DeepscribeTranscriber(PredictiveModel):

    def __init__(self,settings):
        self.cfg = TranscribeConfig()
        self.inf_cfg = self.cfg.inference
        self.device = torch.device("cuda" if self.inf_cfg.hardware.cuda else "cpu")
        self.model = load_model(
            model_path=settings['model_path'],
            precision=self.inf_cfg.hardware.precision,
            device=self.device)
        self.decoder = load_decoder(
            decoder_cfg=self.inf_cfg.decoder,
            labels=self.model.labels)

    def predict(self,input_path):
        return run_inference(
            input_path=input_path,
            model=self.model,
            decoder=self.decoder,
            cfg=self.inf_cfg,
            device=self.device)

