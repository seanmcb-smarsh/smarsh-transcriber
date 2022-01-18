#!/bin/bash

source $(dirname $0)/common_download.sh

FILES="BinaryTestDataSandbox/audio/LABS-1204/fightclub_with_silence.wav BinaryTestDataSandbox/audio/LABS-1204/Conversation01_8kWAV.wav BinaryTestDataSandbox/audio/LABS-1204/005sec-remainder.wav BinaryTestDataSandbox/audio/Unigy_UnigyNode_114870-100Secs.wav"

DESTINATION="tests/test_audio/wav/downloaded"

download_files "$FILES" "$DESTINATION"

exit 0
