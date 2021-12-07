from unittest import TestCase

import api.transcribers
import api.language_identifiers
import api.voice_activity_detectors
class Test(TestCase):

    def test_transcribe(self):
        transcriber = transcriber_factory('example_configs/transcription/english.yaml')
        result = transcriber.predict('data/english.wav')
        print(result["data/english.wav"]["transcription"])

    def test_lid(self):
        lid = lid_factory('example_configs/classification/lid.yaml')
        result = lid.predict('data/english.wav')
        print(result["data/english.wav"]["label"])

    def test_lid_intervals(self):
        lid = lid_factory('example_configs/classification/lid_intervals.yaml')
        result = lid.predict({'data/english.wav':[[0, 5], [6, 10]])
        print(result["data/english.wav"]["label"])

    def test_vad(self):
        vad = vad_factory('example_configs/classification/vad.yaml')
        result = vad.predict('data/english.wav')
        print(result["data/english.wav"]["intervals"])
