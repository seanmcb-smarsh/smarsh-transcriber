import os
import sys
import torch
from abc import ABC, abstractmethod
from typing import Dict, Union, List
import numpy as np
from munch import DefaultMunch


def load(settings):

        load.settings = settings

        load.transcriber = settings.get('transcriber',{})
  
        return(str_to_class(load.transcriber))


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)

class TranscriberModel(ABC):
    
    @abstractmethod
    def predict(self, x: Union[str, List[str]]) -> List[Dict[str, Union[str, np.ndarray, List[str]]]]:
        pass


    @staticmethod
    def load(path: str, class_name: str, module_name: str):
        pass


class deepscribe(TranscriberModel):


    def predict(input_path): 

        # DeepScribe-specific imports
        from deepscribe_inference.config import TranscribeConfig,HardwareConfig,InferenceConfig
        from deepscribe_inference.load_model import load_model, load_decoder
        from deepscribe_inference.transcribe import run_inference 

        new_model=load.settings['model_path']

        config_dict=TranscribeConfig.inference.__dict__
        audio_model=load.settings['model_path']

        # Update config dictionary
        if audio_model: config_dict['model'].model_path=audio_model
        if load.settings.get('lm_path',{}): config_dict['decoder'].lm_path=load.settings['lm_path']
        if load.settings.get('punc_path',{}): config_dict['text_postprocessing'].punc_path=load.settings['punc_path']
        #config_dict['text_postprocessing'].punc_path=load.settings['punc_path'] #Without Null test
        
        if load.settings.get('acronyms_path',{}): config_dict['text_postprocessing'].acronyms_path=load.settings['acronyms_path']
        
        #config_dict['decoder'].lm_path=load.settings['lm_path']
        if load.settings.get('alpha',{}): config_dict['decoder'].lm_alpha=load.settings['alpha']
        if load.settings.get('beta',{}): config_dict['decoder'].lm_alpha=load.settings['beta']
        
        #Local config or default device:
        if load.settings.get('device',{}):device=load.settings['device']

        # Convert updated dictionary to object
        cfg=DefaultMunch.fromDict(config_dict)

        #Locall config device or default
        if device: 
            device=torch.device(device)
        else:
            device = torch.device("cuda" if config_dict['hardware'].cuda else "cpu")

        #run_inference parameters
        
        model = load_model(model_path=audio_model, precision=HardwareConfig.precision, device=device)

        decoder = load_decoder(decoder_cfg=InferenceConfig.decoder,labels=model.labels)

        return run_inference(input_path=input_path, model=model,decoder=decoder,cfg=cfg,device=device)

    
#----------------------------------------------------------------------------------------------------
# Test Class for Hubert - Not for implementation
#----------------------------------------------------------------------------------------------------
# class hubert(TranscriberModel):


#     def predict(input_path):

#         print('I am HuBERT')
#         print('Input',input_path)
#         print('Settings',load.settings)

#         return('HuBERT returning your call')

