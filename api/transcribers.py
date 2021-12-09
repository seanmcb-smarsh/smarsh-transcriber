import torch


from deepscribe_inference.load_model import load_model, load_decoder
from deepscribe_inference.transcribe import run_inference
from dataclasses import dataclass
from importlib import import_module
from typing import Iterable, Mapping

def transcriber_factory(config):
    """
    Factory to produce Transcribers.
    Passed a config object, it returns a Transcriber ready to go.
    The Transcriber will have been initialized and loaded with all models,
    and be ready to convert speech into text.

    :param config: Config object containing parameters common to all transcribers

    The config object is Duck Typed.  It doesn't matter what kind of
    object it is, provided it has the required fields.  They are:

    transcriber: string class name of the Transcriber engine e.g. DeepscribeTranscriber
    config: a config object specific to the Transcriber engine e.g. a Deepscribe InferenceConfig
    """
    comps = config.transcriber.split('.')
    clz = getattr(import_module('api.transcribers'), comps[0])
    for comp in comps[1:]:
        clz = getattr(clz, comp)
    return clz(config.config)

@dataclass
class TranscriptionToken:
    text: str
    start_time: int
    end_time: int

@dataclass
class TranscriptionResult:
    tokens: Iterable[TranscriptionToken]

class DeepscribeTranscriber():
    """
    Internal implementation of Transcriber API to Deepscribe.  Only accessed via transcriber_factory()
    """
    def __init__(self,inference_config):
        """

        :param inference_config: Config object containing parameters specific to the DeepscribeTranscriber

        The inference_config object is Duck Typed.  It doesn't matter what kind of
        object it is, provided it has the required fields.  To allow complete control,
        the config is expected to conform to a Deepscribe InferenceConfig class.  Described here:

        https://git.corp.digitalreasoning.com/projects/LABS/repos/deepscribe-inference/browse/deepscribe_inference/config.py

        @dataclass
        class InferenceConfig:
            decoder: DecoderConfig = DecoderConfig()
            text_postprocessing: TextPostProcessingConfig = TextPostProcessingConfig()
            data: DataConfig = DataConfig()
            model: SavedModelConfig = SavedModelConfig()
            output: OutputConfig = OutputConfig()
            hardware: HardwareConfig = HardwareConfig()
            verbose: bool = True  # Verbosity of logging

        @dataclass
        class DecoderConfig:
            lm_path: str = ''  # Path to an (optional) kenlm language model for use with beam search
            alpha: float = 0.39  # Language model weight Default is tuned for English
            beta: float = 0.45  # Language model word bonus (all words) Default is tuned for English
            cutoff_top_n: int = 40  # Keep top cutoff_top_n characters with highest probs in beam search
            cutoff_prob: float = 1.0  # Cutoff probability in pruning. 1.0 means no pruning
            lm_workers: int = 8  # Number of LM processes to use for beam search
            beam_width: int = 32  # Beam width to use for beam search
            decoder: DecoderType = DecoderType.greedy  # Decoder type to use (automatically set to beam when lm_path specified)

        @dataclass
        class TextPostProcessingConfig:
            punc_path: str = ''  # Path to a DeepScribe Punctuation model
            acronyms_path: str = ''  # Path to acronym whitelist (collapse and capitalize)

        @dataclass
        class SavedModelConfig:
            model_path: str = ''  # Path to acoustic model
            train_manifest_path: str = ''  # Path to a manifest that was used to train the model

        @dataclass()
        class HardwareConfig:
            cuda: bool = True  # Use CUDA for inference
            precision: ModelPrecision = ModelPrecision.half  # Precision for CUDA inference

        The InterfaceConfig has many values, however default values are provided for all of them.
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
        self.inf_cfg = inference_config
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

