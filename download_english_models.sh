#!/bin/bash

source $(dirname $0)/common_download.sh

FILES="all.acronyms.txt deepscribe-0.3.0.pth financial-0.1.3.trie punc-0.2.0.pth"
ARTIFACTORY_REPO="BinaryTestDataSandbox"
MODELS_HOME="audio/models/en"
FINAL_DESTINATION="models"
ARTIFACTORY_HOSTNAME=${ARTIFACTORY_HOSTNAME:-"artifacts.corp.digitalreasoning.com"}
REMOTE_HOME="https://$ARTIFACTORY_HOSTNAME/artifactory/$ARTIFACTORY_REPO/$MODELS_HOME"
ARTIFACTORY_API="https://$ARTIFACTORY_HOSTNAME/artifactory/api/storage/$ARTIFACTORY_REPO/$MODELS_HOME"


mkdir -p $MODELS_HOME
for FILE in $FILES;
do
    echo "$FILE:"
    FILE_URL="$REMOTE_HOME/$FILE"
    CHECKSUMS=$($CURL_CMD -s "$ARTIFACTORY_API/$FILE" | jq '.checksums')
    if [ "$CHECKSUMS" == "null" ]; then
        echo "$FILE_URL does not exist. Artifactory API call to $ARTIFACTORY_API/$FILE failed"
        exit 1
    fi

    DESTINATION="$MODELS_HOME/$FILE"
    if ! checksums "$DESTINATION" "$CHECKSUMS" "$FILE_URL"; then
        $CURL_CMD "$FILE_URL" -o "$FINAL_DESTINATION/$FILE"
        if ! checksums "$FINAL_DESTINATION/$FILE" "$CHECKSUMS" "$FILE_URL"; then
            echo "Failed to download $FILE from $FILE_URL to $DESTINATION"
            exit 1
        fi
    fi
done
exit 0