import hydra
from hydra.experimental import initialize, compose
from hydra.utils import to_absolute_path
from hydra.core.config_store import ConfigStore

from deepscribe_inference.config import TranscribeConfig
from deepscribe_inference.config import InferenceConfig, DecoderConfig, HardwareConfig, TextPostProcessingConfig, \
    SavedModelConfig
from deepscribe_inference.load_model import load_model, load_decoder
from deepscribe_inference.transcribe import transcribe, run_inference

from api.transcriber_api import TranscriberModel
import json
import os
import io
from typing import Dict, List,Optional
import yaml
import sys
import torch



#class deepscribe(TranscriberModel): # Use for dev if you want multiple transcrbers available
class Transcriber(TranscriberModel): 

    cs = ConfigStore.instance()
    cs.store(name="config", node=TranscribeConfig)
    overrides_cfg=to_absolute_path('api/overrides.yaml') # Default - can be overridden below 
    transcriber_name = 'deepscribe'


    def __init__(self,*args, **kwargs):
        
        config=TranscribeConfig
        self.override_config = kwargs.get('overrides',{})
        overrides_cfg=self.override_config


    def load(self):

        overrides=[]

        def path_check(path_key,check_path):
            path_dict={'self.input_path':'[]','self.output_path':"''"}

            path_type = [key for key, value in path_dict.items() if path_key in key]

            return path_type,check_path


        # Refactor   
        def local_overrides(config_file): 

            out_file = ''
            filepaths=['input_path','output_path'] # Probably not set in config but passed directly - but check before overwriting

            transcriber=self.transcriber_name
            with open(config_file, "r") as configs:
                all_settings = yaml.load(configs, Loader=yaml.FullLoader)
                transcriber_settings = all_settings.get('config',{}).get('transcriber',{}).get(transcriber,{}) 
                lang = transcriber_settings.get('config',{}).get('language',{})
                settings = transcriber_settings.get('config',{}).get('models',{}).get(lang,{})
                local_overrides=[]
                for k in settings:
                    if settings[k] not in (None,''):

                        if k in filepaths:
                            v,p = path_check(k,settings[k])
                            if k =='input_path':
                                if self.input_path:
                                    local_overrides.append('input_path' +'='+ str(self.input_path))
                                    continue
                            if k=='output_path':
                                if self.output_path:
                                    local_overrides.append('output_path' +'='+ str(self.output_path))
                                    continue
                        local_overrides.append(k +'='+ str(settings[k]))

                # The next set of settings are for all languages. They can be removed in the config file and applied per langauge if preferred
                # The code does not need to change as nulls will be returned and ignored.

                data_settings = transcriber_settings.get('data',{})
                for k in data_settings:
                    if data_settings[k] not in (None,''):
                        local_overrides.append(k +'='+ str(data_settings[k]))
                self.overrides=local_overrides

                return local_overrides

        overrides=local_overrides(self.overrides_cfg)


    def predict(self,*args,**kwargs): 

        #Allow file inputs and outputs to be set when called
        self.input_path = kwargs.get('input_path',{})
        self.output_path = kwargs.get('output_path',{})
        if kwargs.get('config',{}) == {}:
            self.config=self.override_config   #Overrides already supplied at instantiation
        else:
            self.config = kwargs.get('config',{}) # Overrides supplied on calling predict
        print('*** CONFIG', self.config)
        
        @hydra.main(config_name="config")
        def hydra_main(cfg: TranscribeConfig):

            cfg=compose(config_name="config",overrides=self.overrides) # hydra compose overrides with config
            #print('*** CONFIG ***\n',cfg)  #Dev check on config contents
            transcribe(cfg=cfg)

            return

        self.load()
        hydra_main()

    def run(self):          #Alternative command to 'predict' (if preferred)
        self.predict()





#----------------------------------------------------------------------------------------------------
# Test Class for Hubert - Not for implementation
#----------------------------------------------------------------------------------------------------
'''
class Transcriber(TranscriberModel): 
#class hubert(TranscriberModel): Use for dev if you want multiple transcrbers available

    #transcriber_name = __qualname__
    transcriber_name = 'hubert'

    def __init__(self,*args, **kwargs):
        print('Initialise Hubert Model')

    def predict(self,*args,**kwargs): 
        
        print('\nHubert Config\n')
        
        def local_overrides(config_file): 

            out_file = ''
            filepaths=['input_path','output_path'] # Probably not set in config but passed directly - but check before overwriting

            transcriber=self.transcriber_name
            with open(config_file, "r") as configs:
                all_settings = yaml.load(configs, Loader=yaml.FullLoader)
                transcriber_settings = all_settings.get('config',{}).get('transcriber',{}).get(transcriber,{}) 
                lang = transcriber_settings.get('config',{}).get('language',{})
                settings = transcriber_settings.get('config',{}).get('models',{}).get(lang,{})
                local_overrides=[]
                for k in settings:
                    if settings[k] not in (None,''):

                        if k in filepaths:
                            v,p = path_check(k,settings[k])
                            if k =='input_path':
                                if self.input_path:
                                    local_overrides.append('input_path' +'='+ str(self.input_path))
                                    continue
                            if k=='output_path':
                                if self.output_path:
                                    local_overrides.append('output_path' +'='+ str(self.output_path))
                                    continue
                        local_overrides.append(k +'='+ str(settings[k]))
                print(local_overrides)
                # The next set of settings are for all languages. They can be removed in the config file and applied per langauge if preferred
                # The code does not need to change as nulls will be returned and ignored.
                data_settings = transcriber_settings.get('data',{})
                for k in data_settings:
                    if data_settings[k] not in (None,''):
                        local_overrides.append(k +'='+ str(data_settings[k]))
                self.overrides=local_overrides

                return local_overrides
        
        print(local_overrides('api/overrides.yaml'))

        print('Hubert Predictions')
        sys.exit()

# Test Hubert Transcriber
# class Transcriber(hubert):

#     def __init__(self):
#         pass

'''






