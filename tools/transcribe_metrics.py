__copyright__ = "Copyright (C) 2021, Smarsh, All rights reserved"

import sys
import json
from generateMatrices.textProcessing.textProcessing import TextProcessing
from generateMatrices.wrapper.calculateMatricesAlignment import *
from generateMatrices.wrapper.calculateMatricesJiwer import *
from generateMatrices.textProcessing.textProcessing import TextProcessing
from generateMatrices.matricesGenerator import GenerateMatrices

jsonl_file = sys.argv[1]
lang = sys.argv[2]
truths = []
trans = []
with open(jsonl_file,'r') as inp:
    for line in inp.readlines():
        l = json.loads(line)
        truths.append(TextProcessing().process_text(l['truth'], lang))
        trans.append(TextProcessing().process_text(l['transcription'], lang))
        #print(TextProcessing().process_text(l['truth'],lang))
        #print(TextProcessing().process_text(l['transcription'],lang))

print("WER =",GenerateMatrices(lang)(truths, trans).WER)

