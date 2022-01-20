#!/bin/bash

source $(dirname $0)/common_download.sh

FILES="BinaryTestDataSandbox/audio/models/jp/deepscribe-jp-0.1.1.pth BinaryTestDataSandbox/audio/models/jp/japanese-0.1.0.trie"

DESTINATION="models"

download_files "$FILES" "$DESTINATION"

exit 0
