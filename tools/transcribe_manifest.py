import json

from api.transcribers import DeepscribeConfig, DeepscribeDecoderConfig, DeepscribeModelConfig, \
    DeepscribeTextPostProcessingConfig

cfg = DeepscribeConfig(
    decoder=DeepscribeDecoderConfig(
        lm_path="tests/test_models/en/financial-0.1.3.trie",
        lm_workers=2
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
with open("/audio-data/datasets/english/test/commonvoice_v1/mozilla_valid/mozilla_valid_test.jsonl","r") as f:
    l = list(f)
    for s in l:
        x = json.loads(s)
        r = transcriber.predict(x["speech_path"])
        with open(x["text_path"]) as ft:
            txt = ft.read()
            print(r[x["speech_path"]].tokens,txt)
