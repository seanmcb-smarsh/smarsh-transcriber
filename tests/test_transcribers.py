from unittest import TestCase

from api.transcribers import DeepscribeConfig, DeepscribeDecoderConfig, DeepscribeTextPostProcessingConfig, DeepscribeModelConfig

def validate_result(result):
    for input in result.keys():
        prev_end = -1
        for token in result[input].tokens:
            print(token)
            assert type(token.text)==str
            assert type(token.start_time)==int
            assert type(token.end_time)==int
            assert len(token.text) > 0
            assert token.end_time > token.start_time
            assert token.start_time > prev_end
            prev_end = token.end_time
            
class Test(TestCase):

    def test_transcribe(self):
        cfg = DeepscribeConfig(
            decoder=DeepscribeDecoderConfig(
                lm_path = "tests/test_models/en/financial-0.1.3.trie",
                lm_workers = 2
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
        input = "tests/the_cat_in_the_hat.wav" 
        result = transcriber.predict(input)
        validate_result(result)

