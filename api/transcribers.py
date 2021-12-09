import torch

from deepscribe_inference.load_model import load_model, load_decoder
from deepscribe_inference.transcribe import run_inference
from dataclasses import dataclass
from importlib import import_module
from typing import Iterable, Mapping

@dataclass
class DeepscribeDecoderConfig:
    lm_path: str = ''  # Path to an (optional) kenlm language model for use with beam search
    alpha: float = 0.39  # Language model weight Default is tuned for English
    beta: float = 0.45  # Language model word bonus (all words) Default is tuned for English
    cutoff_top_n: int = 40  # Keep top cutoff_top_n characters with highest probs in beam search
    cutoff_prob: float = 1.0  # Cutoff probability in pruning. 1.0 means no pruning
    lm_workers: int = 8  # Number of LM processes to use for beam search
    beam_width: int = 32  # Beam width to use for beam search

@dataclass
class DeepscribeTextPostProcessingConfig:
    punc_path: str = ''  # Path to a DeepScribe Punctuation model
    acronyms_path: str = ''  # Path to acronym whitelist (collapse and capitalize)

@dataclass
class DeepscribeModelConfig:
    model_path: str = ''  # Path to acoustic model

@dataclass()
class DeepscribeHardwareConfig:
    cuda: bool = True  # Use CUDA for inference

@dataclass
class DeepscribeConfig:
    decoder: DeepscribeDecoderConfig = DeepscribeDecoderConfig()
    text_postprocessing: DeepscribeTextPostProcessingConfig = DeepscribeTextPostProcessingConfig()
    model: DeepscribeModelConfig = DeepscribeModelConfig()
    hardware: DeepscribeHardwareConfig = DeepscribeHardwareConfig()

@dataclass
class Wav2VecConfig:
    dummy: str = "dummy"

@dataclass
class AWSConfig:
    another_dummy: str = "dummy"

def transcriber_factory(config: Union[DeepscribeConfig,Wav2VecConfig,AWSConfig]):
    """
    Factory to produce Transcribers.
    Passed a config object, it returns a Transcriber ready to go.
    The Transcriber will have been initialized and loaded with all models,
    and be ready to convert speech into text.

    :param config: Config object containing parameters specifying the desired transcriber

    The the type of the config object specifies the transcriber engine to be created.
    For example, passing an instance of DeepscribeConfig will return transcriber_factory initalized
    DeepscribeTranscriber
    """
    name = config.__class__.__name__
    if name == 'DeepscribeConfig':
        return DeepscribeTranscriber(config)
    else:
        raise NotImplementedError(name + ' is not implemented')


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
        hardware.cuda: boolean specify whether the engine should run on a GPU e.g. true
        """
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
                cuda = config.hardware.cuda
            )
        )
        self.device = torch.device("cuda" if self.inf_cfg.hardware.cuda else "cpu")
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
            text = list(raw_results[input]['transcript'])
            times = [0] + raw_results[input]['timestamps']
            results = []
            for i in range(len(text)):
                results.append(TranscriptionToken(text=text[i], start_time=times[i], end_time=times[i+1]))
            final_results.update({input: TranscriptionResult(results)})
        return final_results

