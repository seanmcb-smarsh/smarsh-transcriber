#!/bin/bash

source $(dirname $0)/common_download.sh

FILES="BinaryTestDataSandbox/audio/models/cn/deepscribe-cn-0.2.1.pth"

DESTINATION="models"

download_files "$FILES" "$DESTINATION"

exit 0
