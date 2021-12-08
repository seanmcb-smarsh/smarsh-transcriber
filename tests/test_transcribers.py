from unittest import TestCase

from api.transcribers import transcriber_factory
from api.util.configs import read_config

class Test(TestCase):

    def test_transcribe(self):
        cfg = read_config('tests/test_models/en/english.yaml')
        transcriber = transcriber_factory(cfg)
        input = "tests/test_audio/wav/downloaded/fightclub_with_silence.wav"
        result = transcriber.predict([input])
        for token in result[input].tokens:
            print(token.text,token.start_time,token.end_time)

    # def test_lid(self):
    #     lid = lid_factory('example_configs/lid.yaml')
    #     result = lid.predict('data/english.wav')
    #     print(result["data/english.wav"]["label"])
    #
    # def test_lid_intervals(self):
    #     lid = lid_factory('example_configs/lid_intervals.yaml')
    #     result = lid.predict({'data/english.wav':[[0, 5], [6, 10]])
    #     print(result["data/english.wav"]["label"])
    #
    # def test_vad(self):
    #     vad = vad_factory('example_configs/vad.yaml')
    #     result = vad.predict('data/english.wav')
    #     print(result["data/english.wav"]["intervals"])
