#!/bin/bash

source $(dirname $0)/common_download.sh

FILES="LABS-1204/fightclub_with_silence.wav LABS-1204/Conversation01_8kWAV.wav LABS-1204/005sec-remainder.wav Unigy_UnigyNode_114870-100Secs.wav"
ARTIFACTORY_REPO="BinaryTestDataSandbox/audio/"
AUDIO_HOME="tests/test_audio/wav/downloaded"
ARTIFACTORY_HOSTNAME=${ARTIFACTORY_HOSTNAME:-"artifacts.corp.digitalreasoning.com"}
REMOTE_HOME="https://$ARTIFACTORY_HOSTNAME/artifactory/$ARTIFACTORY_REPO"
ARTIFACTORY_API="https://$ARTIFACTORY_HOSTNAME/artifactory/api/storage/$ARTIFACTORY_REPO/"

mkdir -p $AUDIO_HOME
for FILE in $FILES;
do
    echo "$FILE:"
    FILE_URL="$REMOTE_HOME/$FILE"
    CHECKSUMS=$($CURL_CMD -s "$ARTIFACTORY_API/$FILE" | jq '.checksums')
    if [ "$CHECKSUMS" == "null" ]; then
        echo "$FILE_URL does not exist. Artifactory API call to $ARTIFACTORY_API/$FILE failed"
        exit 1
    fi

    DESTINATION="$AUDIO_HOME/$(basename $FILE)"
    if ! checksums "$DESTINATION" "$CHECKSUMS" "$FILE_URL"; then
        $CURL_CMD "$FILE_URL" -o "$DESTINATION"
        if ! checksums "$DESTINATION" "$CHECKSUMS" "$FILE_URL"; then
            echo "Failed to download $FILE from $FILE_URL to $DESTINATION"
            exit 1
        fi
    fi
done
exit 0
