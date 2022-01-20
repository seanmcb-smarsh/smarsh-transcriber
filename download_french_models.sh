#!/bin/bash

source $(dirname $0)/common_download.sh

FILES="BinaryTestDataSandbox/audio/models/fr/deepscribe-fr-0.1.2.pth BinaryTestDataSandbox/audio/models/fr/french-0.1.0.trie BinaryTestDataSandbox/audio/models/fr/punc-fr-0.1.0.pth"

DESTINATION="models"

download_files "$FILES" "$DESTINATION"

exit 0
