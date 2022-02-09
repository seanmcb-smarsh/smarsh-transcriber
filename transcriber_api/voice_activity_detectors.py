
import yaml

from lang_id_api.models.voice_activity_detection import SpeechbrainVAD
from trellis import PredictiveModel


def vad_factory(yaml_file):
    with open(yaml_file, "r") as configs:
        settings = yaml.load(configs, Loader=yaml.FullLoader)
        comps = settings["voice_activity_detector"].split('.')
        clz = globals()[comps[0]]
        for comp in comps[1:]:
            clz = getattr(clz, comp)
        return clz(settings)


class SpeechbrainVoiceActivityDetector(SpeechbrainVAD, PredictiveModel):

    def __init__(self, settings):
        super(SpeechbrainVoiceActivityDetector, self).__init__(device=settings["device"], model_path=settings["model_path"])

    def predict(self, wavs):
        return super(SpeechbrainVoiceActivityDetectorr, self).predict(wavs)


