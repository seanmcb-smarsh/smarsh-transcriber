from unittest import TestCase

import api.transcribers

class Test(TestCase):

    def test_load(self):
        transcriber = api.transcribers.load('example_configs/english.yaml')

    def test_predict(self):
        transcriber = transcriber_factory('example_configs/english.yaml')
        result = transcriber.predict('data/english.wav')
        print(result["data/english.wav"]["transcription"])

    def test_lid(self):
        lid = lid_factory('example_configs/lid.yaml')
        result = lid.predict('data/english.wav')
        print(result["data/english.wav"]["label"])

    def test_vad(self):
        vad = vad_factory('example_configs/vad.yaml')
        result = vad.predict('data/english.wav')
        print(result["data/english.wav"]["intervals"])
