#!/bin/bash

source $(dirname $0)/common_download.sh

FILES="BinaryTestDataSandbox/audio/models/en/all.acronyms.txt BinaryTestDataSandbox/audio/models/en/deepscribe-0.3.0.pth BinaryTestDataSandbox/audio/models/en/financial-0.1.3.trie BinaryTestDataSandbox/audio/models/en/punc-0.2.0.pth"

DESTINATION="models"

download_files "$FILES" "$DESTINATION"

exit 0
