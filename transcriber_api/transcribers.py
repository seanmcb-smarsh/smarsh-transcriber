__copyright__ = "Copyright (C) 2021, Smarsh, All rights reserved"

import torch
import yaml

from deepscribe_inference.load_model import load_model, load_decoder
from deepscribe_inference.transcribe import run_inference
from deepscribe_inference.config import InferenceConfig, DecoderConfig, TextPostProcessingConfig, SavedModelConfig, HardwareConfig, DataConfig
from dataclasses import dataclass
from typing import List, Iterable, Mapping, Union
from pydantic import BaseModel
from abc import abstractmethod
import logging

class ITranscriberConfig(BaseModel):
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

class DeepscribeDataConfig(BaseModel):
    batch_size: int = 32
    num_workers: int = 8
    hard_split_seconds: float = 0

class DeepscribeConfig(ITranscriberConfig):
    language = 'language must be specified'
    decoder = DeepscribeDecoderConfig()
    text_postprocessing = DeepscribeTextPostProcessingConfig()
    model = DeepscribeModelConfig()
    hardware = DeepscribeHardwareConfig()
    data = DeepscribeDataConfig()

    def load(self):
        return DeepscribeTranscriber(self)

class Wav2VecConfig(ITranscriberConfig):
    def load(self):
        raise NotImplementedError('Wav2Vec is not implemented')

class AWSConfig(ITranscriberConfig):
    def load(self):
        raise NotImplementedError('AWS is not implemented')


TranscriberConfig = Union[DeepscribeConfig, Wav2VecConfig, AWSConfig]


def load_yaml(yaml_file: str):
    with open(yaml_file, "r") as y:
        dict = yaml.load(y,Loader=yaml.FullLoader)
        if len(dict.keys()) != 1:
            raise RuntimeError("Configuration can only specify 1 type of Transcriber")
        clz = list(dict.keys())[0]
        args = dict[clz]
        try:
            cfg = globals()[clz](**args)
            return cfg.load()
        except KeyError:
            raise RuntimeError("Unknown Transcriber: '"+clz+"'")


@dataclass
class TranscriptionOffset:
    """
    Common representation of word or punctuation in a transcription
    """
    starting_text_offset: int       # orthography or word or punctuation
    starting_audio_offset: int      # start time in milliseconds

@dataclass
class TranscriptionResult:
    """
    Common transcription result.  Returned by all types of transcribers
    """
    transcription: str
    offsets: List[TranscriptionOffset] # sequence of words or punctuation
    duration: float = 0.0 # length of audio in seconds
    score: float = 0.0

WordLanguages = ['en','fr','sp']
CharLanguages = ['cn','jp','hk']

class DeepscribeTranscriber:
    """
    Internal implementation of Transcriber API to Deepscribe.  Only accessed via transcriber_factory()
    """
    def __init__(self, config: DeepscribeConfig):
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
        self.transcriber_name = self.__class__.__name__
        self._log = logging.getLogger(self.transcriber_name)

        self.language = config.language
        if not self.language in WordLanguages and not self.language in CharLanguages:
            raise NotImplementedError('Language not implemented: '+self.language)

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
            ),
            data = DataConfig(
                batch_size=config.data.batch_size,
                hard_split_seconds=config.data.hard_split_seconds,
                num_workers=config.data.num_workers,
            ),
        )
        self.device = torch.device(dev)
        self.model = load_model(
            model_path=self.inf_cfg.model.model_path,
            precision=self.inf_cfg.hardware.precision,
            device=self.device)
        self.decoder = load_decoder(
            decoder_cfg=self.inf_cfg.decoder,
            labels=self.model.labels)

        self._log.info(f"Initialised {self.transcriber_name} using config: {self.inf_cfg}, device: {dev}")



    def _word_result(self, text, times, duration, score):
        in_word = False
        offsets = []
        current_text_offset = 0
        for ch, tm in zip(text, times):

            if ch == ' ':
                # we just finished a word
                in_word = False
            elif not in_word:
                # we are starting a new word
                starting_audio_offset = int(1000 * float(tm))
                in_word = True
                offsets.append(TranscriptionOffset(starting_text_offset=current_text_offset, starting_audio_offset=starting_audio_offset))
            # else we are inside a word

            current_text_offset = current_text_offset + 1

        return TranscriptionResult(text, offsets, duration, score)

    def _char_result(self, text, times, duration, score):
        tokens = []
        current_text_offset = 0

        for ch, tm in zip(text, times):
            current_audio_offset = int(1000 * float(tm))
            tokens.append(TranscriptionOffset(starting_text_offset=current_text_offset, starting_audio_offset=current_audio_offset))
            current_text_offset = current_text_offset + 1

        return TranscriptionResult(text, tokens, duration, score)

    def _process_result(self,raw_result):
        text = raw_result['transcript']
        times = raw_result['timestamps']
        duration = raw_result['duration']
        duration = duration if duration is not None else 0.0
        score = raw_result['score']
        score = score if score is not None else 0.0
        assert len(text) == len(times)
        return self._word_result(text, times, duration, score) if self.language in WordLanguages else self._char_result(text, times, duration, score)

    def predict(self,input_paths: Iterable[str]) -> Mapping[str, TranscriptionResult]:
        """
        Convert audio recordings into transcriptions.

        :param input_paths: An iterable collection of string file paths.  Paths are expected to be WAV files
        :return: a Mapping of file path to TranscriptionResult

        @dataclass
        class TranscriptionOffset:
            starting_text_offset: int
            starting_audio_offset: int

        @dataclass
        class TranscriptionResult:
            transcription: str
            offsets: List[TranscriptionOffset]
            duration: float
            score: float

        Example of result:

        TranscriptionResult(
            transcription="The cat in the hat",
            offsets=[
                TranscriptionOffset(starting_text_offset=0, starting_audio_offset=240)
                TranscriptionOffset(starting_text_offset=4, starting_audio_offset=480)
                TranscriptionOffset(starting_text_offset=8, starting_audio_offset=880)
                TranscriptionOffset(starting_text_offset=11, starting_audio_offset=1040)
                TranscriptionOffset(starting_text_offset=15, starting_audio_offset=1220)
            ],
            duration=1.6370068027210884,
            score=1.0)
        """
        if isinstance(input_paths, str):
            input_paths = [input_paths]
        raw_results = run_inference(
            input_path=input_paths,
            model=self.model,
            decoder=self.decoder,
            cfg=self.inf_cfg,
            device=self.device)
        return {input: self._process_result(raw_results[input]) for input in input_paths}



