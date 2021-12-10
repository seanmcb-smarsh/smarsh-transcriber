from unittest import TestCase

from api.transcribers import transcriber_factory, DeepscribeConfig, DeepscribeDecoderConfig, DeepscribeTextPostProcessingConfig, DeepscribeModelConfig

class Test(TestCase):

    def test_transcribe(self):
        cfg = DeepscribeConfig(
            decoder=DeepscribeDecoderConfig(
                lm_path = "/share/models/english/financial-0.1.3.trie"
            ),
            model=DeepscribeModelConfig(
                model_path="/share/models/english/deepscribe-0.3.0.pth"
            ),
            text_postprocessing=DeepscribeTextPostProcessingConfig(
                punc_path="/share/models/english/punc-0.2.0.pth",
                acronyms_path="/share/models/english/acronyms/all.acronyms.txt"
            )
        )
        transcriber = cfg.load()
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
