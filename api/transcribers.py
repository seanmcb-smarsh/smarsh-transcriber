import torch
import yaml

from deepscribe_inference.load_model import load_model, load_decoder
from deepscribe_inference.transcribe import run_inference
from deepscribe_inference.config import InferenceConfig, DecoderConfig, TextPostProcessingConfig, SavedModelConfig, HardwareConfig
from dataclasses import dataclass
from typing import Iterable, Mapping
from pydantic import BaseModel
from abc import abstractmethod

class TranscriberConfig(BaseModel):
    @abstractmethod
    def load(self):
        """
        Common method to return a Transcriber.
        The the type of the config object specifies the transcriber engine to be created.
        For example, calling load() on an instance of DeepscribeConfig will return an initalized
        DeepscribeTranscriber

        :return: a Transcriber ready to go. The Transcriber will have been initialized and loaded with all models,
        and be ready to convert speech into text.
        """
        pass

class DeepscribeDecoderConfig(BaseModel):
    lm_path = ''   # Path to an (optional) kenlm language model for use with beam search
    alpha = 0.39 # Language model weight Default is tuned for English
    beta = 0.45  # Language model word bonus (all words) Default is tuned for English
    cutoff_top_n = 40    # Keep top cutoff_top_n characters with highest probs in beam search
    cutoff_prob = 1.0  # Cutoff probability in pruning. 1.0 means no pruning
    lm_workers = 2  # Number of LM processes to use for beam search
    beam_width = 32 # Beam width to use for beam search

class DeepscribeTextPostProcessingConfig(BaseModel):
    punc_path = ''  # Path to a DeepScribe Punctuation model
    acronyms_path = ''  # Path to acronym whitelist (collapse and capitalize)

class DeepscribeModelConfig(BaseModel):
    model_path = ''  # Path to acoustic model

class DeepscribeHardwareConfig(BaseModel):
    device = ''  # Use CPU or GPU for inference.  If '', use a GPU if is present, otherwise CPU

class DeepscribeConfig(TranscriberConfig):
    decoder = DeepscribeDecoderConfig()
    text_postprocessing = DeepscribeTextPostProcessingConfig()
    model = DeepscribeModelConfig()
    hardware = DeepscribeHardwareConfig()

    def load(self):
        return DeepscribeTranscriber(self)

class Wav2VecConfig(BaseModel):
    def load(self):
        raise NotImplementedError('Wav2Vec is not implemented')

class AWSConfig(BaseModel):
    def load(self):
        raise NotImplementedError('AWS is not implemented')

def load_yaml(yaml_file: str):
    with open(yaml_file, "r") as y:
        dict = yaml.load(y)
        cfg = DeepscribeConfig(dict)
        return cfg.load()


@dataclass
class TranscriptionToken:
    """
    Common representation of word or punctuation in a transcription
    """
    text: str       # orthography or word or punctuation
    start_time: int # start time in milliseconds
    end_time: int   # end time in milliseconds

@dataclass
class TranscriptionResult:
    """
    Common transcription result.  Returned by all types of transcribers
    """
    tokens: Iterable[TranscriptionToken] # sequence of words or punctuation

class DeepscribeTranscriber:
    """
    Internal implementation of Transcriber API to Deepscribe.  Only accessed via transcriber_factory()
    """
    def __init__(self,config: DeepscribeConfig):
        """
        :param config: Config object containing parameters specific to the DeepscribeTranscriber

        The DeepscribeConfig has many values, however default values are provided for all of them.
        The caller overrides some of these values using recommendations from Research.
        Some common overrides are:

        model.model_path: string path to acoustic models e.g. "/share/models/english/deepscribe-0.3.0.pth"
        decoder.lm_path: string path to language models e.g. "/share/models/english/financial-0.1.3.trie"
        decoder.alpha: float weight for alpha e.g. 0.39
        decoder.beta: float weight for beta e.g. 0.45
        text_postprocessing.punc_path: string path to punctuation models e.g. "/share/models/english/punc-0.2.0.pth"
        text_postprocessing.acronyms_path: string path to acronyms models e.g. "/share/models/english/acronyms/all.acronyms.txt"
        hardware.device: string specify whether the engine should run on CPU or GPU.  None, "cpu" or "gpu".  If None (default) use a GPU if it is present, otherwise CPU
        """
        if config.hardware.device=='':
            dev = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            dev = config.hardware.device

        self.inf_cfg = InferenceConfig(
            decoder = DecoderConfig(
                lm_path = config.decoder.lm_path,
                alpha = config.decoder.alpha,
                beta = config.decoder.beta,
                cutoff_top_n = config.decoder.cutoff_top_n,
                cutoff_prob = config.decoder.cutoff_prob,
                lm_workers = config.decoder.lm_workers,
                beam_width = config.decoder.beam_width
            ),
            text_postprocessing = TextPostProcessingConfig(
                punc_path = config.text_postprocessing.punc_path,
                acronyms_path = config.text_postprocessing.acronyms_path
            ),
            model = SavedModelConfig(
                model_path = config.model.model_path
            ),
            hardware = HardwareConfig(
                cuda = dev=="cuda"
            )
        )
        self.device = torch.device(dev)
        self.model = load_model(
            model_path=self.inf_cfg.model.model_path,
            precision=self.inf_cfg.hardware.precision,
            device=self.device)
        self.decoder = load_decoder(
            decoder_cfg=self.inf_cfg.decoder,
            labels=self.model.labels)

    def predict(self,input_paths: Iterable[str]) -> Mapping[str, TranscriptionResult]:
        """
        Convert audio recordings into transcriptions.

        :param input_paths: An iterable collection of string file paths.  Paths are expected to be WAV files
        :return: a Mapping of file path to TranscriptionResult

        @dataclass
        class TranscriptionToken:
            text: str
            start_time: int
            end_time: int

        @dataclass
        class TranscriptionResult:
            tokens: Iterable[TranscriptionToken]

        Example of result:

        TranscriptionResult(
            tokens=[
                TranscriptionToken(text='The', start_time=240, end_time=280)
                TranscriptionToken(text='cat', start_time=480, end_time=600)
                TranscriptionToken(text='in', start_time=880, end_time=920)
                TranscriptionToken(text='the', start_time=1040, end_time=1080)
                TranscriptionToken(text='hat.', start_time=1220, end_time=1340)
            ])
        """
        if isinstance(input_paths, str):
            input_paths = [input_paths]
        raw_results = run_inference(
            input_path=input_paths,
            model=self.model,
            decoder=self.decoder,
            cfg=self.inf_cfg,
            device=self.device)

        final_results = {}
        for input in input_paths:
            text = raw_results[input]['transcript']
            times = raw_results[input]['timestamps']
            assert len(text)==len(times)
            in_word = False
            start = 0
            end = 0
            word = ''
            tokens = []
            for ch,tm in zip(text,times):
                if ch==' ' and in_word:
                    # we just finished a word
                    tokens.append(TranscriptionToken(text=word,start_time=start,end_time=end))
                    word = ''
                    in_word = False
                elif not in_word:
                    # we are starting a new word
                    start = int(1000*float(tm))
                    word = word + ch
                    in_word = True
                else:
                    # we are inside a word
                    end = int(1000*float(tm))
                    word = word + ch
            if in_word:
                # final word
                tokens.append(TranscriptionToken(text=word,start_time=start,end_time=end))
            final_results.update({input: TranscriptionResult(tokens)})
        return final_results

