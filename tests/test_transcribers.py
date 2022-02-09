__copyright__ = "Copyright (C) 2021, Smarsh, All rights reserved"

from unittest import TestCase
from transcriber_api.transcribers import load_yaml, TranscriptionResult, TranscriptionOffset


def validate_result(result):
    for input, result in result.items():
        assert type(result) == TranscriptionResult
        assert type(result.transcription) == str
        assert len(result.transcription) > 0
        assert type(result.offsets) == list
        assert len(result.offsets) > 0
        assert type(result.duration) == float
        assert type(result.score) == float
        offset: TranscriptionOffset
        prev_offset = TranscriptionOffset(starting_text_offset=-1, starting_audio_offset=-1)
        for offset in result.offsets:
            assert offset.starting_text_offset > prev_offset.starting_text_offset
            assert offset.starting_audio_offset > prev_offset.starting_audio_offset
            prev_offset = offset

def doit(language,audio):
    transcriber = load_yaml("config/"+language+".yaml")
    input = "tests/"+audio
    result = transcriber.predict(input)
    validate_result(result)

class Test(TestCase):

    def test_english(self):
        doit("english","the_cat_in_the_hat.wav")

    def test_cantonese(self):
        doit("cantonese","the_cat_in_the_hat.wav")

    def test_mandarin(self):
        doit("mandarin","the_cat_in_the_hat.wav")

    def test_japanese(self):
        doit("japanese","the_cat_in_the_hat.wav")

    #def test_spanish(self):
    #    doit("spanish","the_cat_in_the_hat.wav")
    
    def test_sentences_that_start_with_a_single_character_word(self):
        doit("english","a_small_bug.wav")

    def test_conversation01(self):
        doit("english","Conversation01_8kWAV.wav")

    #def test_french(self):
    #    testit("french","the_cat_in_the_hat.wav")