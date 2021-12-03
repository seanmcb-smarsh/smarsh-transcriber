from unittest import TestCase

import api.transcribers

class Test(TestCase):

    def test_load(self):
        transcriber = api.transcribers.load('example_configs/english.yaml')

    def test_predict(self):
        transcriber = api.transcribers.load('example_configs/english.yaml')
        result = transcriber.predict('data/english.wav')
        print(result["transcript"])
