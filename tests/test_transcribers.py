from unittest import TestCase

from api.transcribers import DeepscribeConfig, DeepscribeDecoderConfig, DeepscribeTextPostProcessingConfig, DeepscribeModelConfig

class Test(TestCase):

    def test_transcribe(self):
        cfg = DeepscribeConfig(
            decoder=DeepscribeDecoderConfig(
                lm_path = "tests/test_models/en/financial-0.1.3.trie"
            ),
            model=DeepscribeModelConfig(
                model_path="tests/test_models/en/deepscribe-0.3.0.pth"
            ),
            text_postprocessing=DeepscribeTextPostProcessingConfig(
                punc_path="tests/test_models/en/punc-0.2.0.pth",
                acronyms_path="tests/test_models/en/all.acronyms.txt"
            )
        )
        transcriber = cfg.load()
        input = "tests/test_audio/wav/downloaded/fightclub_with_silence.wav"
        result = transcriber.predict(input)
        for token in result[input].tokens:
            assert type(token.text)==str
            assert type(token.start_time)==int
            assert type(token.end_time)==int
            assert len(token.text) > 0
            assert token.end_time > token.start_time

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
