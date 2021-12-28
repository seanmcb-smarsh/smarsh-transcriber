import json
import sys

from api.transcribers import load_yaml

config_file = sys.args[1]
dataset = sys.args[2]
result = sys.args[3]

transcriber = load_yaml(config_file)

with open(dataset,"r") as inp:
    with open(result, "w") as outp:
        l = list(inp)[:5]
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

