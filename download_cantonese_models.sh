#!/bin/bash

source $(dirname $0)/common_download.sh

FILES="BinaryTestDataSandbox/audio/models/hk/deepscribe-hk-0.1.1.pth"

DESTINATION="models"

download_files "$FILES" "$DESTINATION"

exit 0
