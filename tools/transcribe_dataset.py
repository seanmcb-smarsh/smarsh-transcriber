import json
import sys
import yaml

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

with open(sys.args[1],"r") as y:
    cfg = yaml.load(y)
    o = DeepscribeConfig(cfg)
    print(o)

"""

config_file = sys.args[1]
dataset = sys.args[2]
result = sys.args[3]
transcriber = cfg.load()

with open(dataset,"r") as inp:
    with open(result, "w") as outp:
        l = list(inp)
        for s in l:
            x = json.loads(s)
            wav = x["speech_path"]
            r = transcriber.predict(wav)
            with open(x["text_path"]) as ft:
                txt = ft.read()
                txt2 = ''
                for tok in r[x["speech_path"]].tokens:
                    txt2 = txt2 + tok.text + ' '
                print(txt+' --> '+txt2)
                result_obj = { 'input':wav, 'truth':txt, 'transcription':txt2 }
                result_line = json.dumps(result_obj)
                outp.writelines([result_line])
                """

