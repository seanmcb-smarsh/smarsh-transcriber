__copyright__ = "Copyright (C) 2021, Smarsh, All rights reserved"

import json
import sys

from transcriber_api.transcribers import load_yaml

config_file = sys.argv[1]
dataset = sys.argv[2]
result = sys.argv[3]

transcriber = load_yaml(config_file)

with open(dataset,"r") as inp:
    with open(result, "w") as outp:
        l = list(inp)
        for s in l:
            x = json.loads(s)
            wav = x["speech_path"]
            r = transcriber.predict(wav)
            with open(x["text_path"]) as ft:
                txt = ft.read()
                txt2 = r[x["speech_path"]].transcription
                print(txt+' --> '+txt2)
                result_obj = { 'input':wav, 'truth':txt, 'transcription':txt2 }
                result_line = json.dumps(result_obj)
                outp.write(result_line+'\n')
                outp.flush()
