import yaml

from lang_id_api.models.language_identification import SpeechbrainLID, SpeechbrainLID_Intervals
from trellis import PredictiveModel

def lid_factory(yaml_file):
    with open(yaml_file, "r") as configs:
        settings = yaml.load(configs, Loader=yaml.FullLoader)
        comps = settings["language_identifier"].split('.')
        clz = __import__(comps[0])
        for comp in comps[1:]:
            clz = getattr(clz, comp)
        return clz(settings)

class SpeechbrainLanguageIdentifier(SpeechbrainLID, PredictiveModel):

    def __init__(self,settings):
        super(SpeechbrainLanguageIdentifier, self).__init__(device = settings["device"], batch_size=settings["batch_size"], model_path=settings["model_path"])

    def predict(self,wavs):
        return super(SpeechbrainLanguageIdentifier, self).predict(wavs)

class SpeechbrainLanguageIdentifierWithIntervals(SpeechbrainLID_Intervals, PredictiveModel):

    def __init__(self,settings):
        super(SpeechbrainLanguageIdentifierWithIntervals, self).__init__(device = settings["device"], batch_size=settings["batch_size"], model_path=settings["model_path"])

    def predict(self,wavs_intervals):
        return super(SpeechbrainLanguageIdentifierWithIntervals, self).predict(wavs_intervals)