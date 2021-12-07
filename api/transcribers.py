import torch
import yaml
from abc import ABC, abstractmethod
from typing import Dict, Union, List, Tuple, Optional
import numpy as np
from deepscribe_inference.config import TranscribeConfig, HardwareConfig, InferenceConfig
from deepscribe_inference.load_model import load_model, load_decoder
from deepscribe_inference.transcribe import run_inference


class PredictiveModel(ABC):
    """
    Abstract model that can be loaded and perform 
    inference with the `predict` method.
    """

    @abstractmethod
    def predict(self, x: Union[str, List[str]]) -> List[Dict[str, Union[str, np.ndarray, List[str]]]]:
        """Model inference

        Args:
            x (Union[str, List[str]]): Model input, string of list of strings
        
        Returns:
            List[Dict[str, Union[str, np.ndarray, List[str]]]]: Dict of prediction results

        Example:
            Input: ["Bonjour! Je m'appelle Alice.", "Hi! My name is Bob."]
            Output: [
                {
                    "text": "Bonjour! Je m'appelle Alice.",
                    "best_label": <class_name>,
                    "confidence": 1.0 - compute_avg_uncertainty(probs),
                    "classifications": [
                        {
                            "class_1": "fr",
                            "score": 0.956
                        },
                        ...,
                        {
                            "class_n": "jp",
                            "score": 0.000002
                        },
                    ]
                },
                {
                    "text": "Hi! My name is Bob.",
                    "best_label": <class_name>,
                    "confidence": 1.0 - compute_avg_uncertainty(probs),
                    "classifications": [
                        {
                            "class_1": "en",
                            "score": 0.982
                        },
                        ...,
                        {
                            "class_n": "jp",
                            "score": 0.000005
                        },
                    ]
                }
            ]
        """
        pass

    @staticmethod
    def load(path: str, class_name: str, module_name: str): 
        """Loads model from a path

        Args:
            path (str): Path to model artifact
            class_name (str): Name of class that will be loaded
            module_name (str): Name of module containing class `class_name`        
        """
        pass

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
        print(settings)
        self.device = torch.device(settings["device"])
        self.model = load_model(
            model_path=settings['model_path'],
            precision=HardwareConfig.precision,
            device=self.device)
        self.decoder = load_decoder(
            decoder_cfg=InferenceConfig.decoder,
            labels=self.model.labels)
        self.cfg=InferenceConfig
        

    def predict(self,input_path):
        return run_inference(
            input_path=input_path,
            model=self.model,
            decoder=self.decoder,
            cfg=self.cfg,
            device=self.device)

