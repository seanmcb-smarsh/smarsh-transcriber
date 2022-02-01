__copyright__ = "Copyright (C) 2021, Smarsh, All rights reserved"

import json
import sys

from api.transcribers import load_yaml

config_file = sys.argv[1]
dataset = sys.argv[2]
result = sys.argv[3]

transcriber = load_yaml(config_file)

with open(dataset,"r") as inp:
    with open(result, "w") as outp:
        l = list(inp)
        for s in l:
            x = s.split()
            wav = x[0]
            r = transcriber.predict(wav)
            with open(x[1]) as ft:
                txt = ft.read()
                txt2 = ''
                for tok in r[wav].tokens:
                    txt2 = txt2 + tok.text + ' '
                print(txt+' --> '+txt2)
                result_obj = { 'input':wav, 'truth':txt, 'transcription':txt2 }
                result_line = json.dumps(result_obj)
                outp.write(result_line+'\n')
                outp.flush()
