#!/bin/bash

source $(dirname $0)/common_download.sh

FILES="BinaryTestDataSandbox/audio/models/es/deepscribe-es-0.1.3.pth BinaryTestDataSandbox/audio/models/es/spanish-0.1.2.trie"

DESTINATION="models"

download_files "$FILES" "$DESTINATION"

exit 0
