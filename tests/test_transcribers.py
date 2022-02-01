__copyright__ = "Copyright (C) 2021, Smarsh, All rights reserved"

from unittest import TestCase

from api.transcribers import load_yaml

def validate_result(result):
    for input in result.keys():
        prev_end = -1
        for token in result[input].tokens:
            print(token)
            assert type(token.text)==str
            assert type(token.start_time)==int
            assert type(token.end_time)==int
            assert len(token.text) > 0
            assert token.end_time >= token.start_time
            assert token.start_time >= prev_end
            prev_end = token.end_time

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

