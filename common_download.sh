export ARTIFACTORY_HOSTNAME=${ARTIFACTORY_HOSTNAME:-"artifacts.corp.digitalreasoning.com"}

CURL_CMD="curl -u $ARTIFACTORY_USERNAME:$ARTIFACTORY_PASSWORD"

MD5_CMD="md5sum"
MD5_FIELD=1
if ! which $MD5_CMD >/dev/null 2>&1; then
    MD5_CMD="md5"
    MD5_FIELD=4
fi

SHA1_CMD="sha1sum"
if ! which $SHA1_CMD >/dev/null 2>&1; then
    SHA1_CMD="shasum"
fi

SHA256_CMD="sha256sum"
if ! which $SHA256_CMD >/dev/null 2>&1; then
    SHA256_CMD="shasum -a 256"
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

checksums() {
    DESTINATION="$1"
    CHECKSUMS="$2"
    FILE_URL="$3"
    if [ -f "$DESTINATION" ]; then

        REMOTE_MD5="$(echo $CHECKSUMS | jq -r '.md5')"
        LOCAL_MD5="$($MD5_CMD $DESTINATION | cut -f $MD5_FIELD -d ' ' )"
        REMOTE_SHA1="$(echo $CHECKSUMS | jq -r '.sha1')"
        LOCAL_SHA1="$($SHA1_CMD $DESTINATION | cut -f 1 -d ' ' )"
        REMOTE_SHA256="$(echo $CHECKSUMS | jq -r '.sha256')"
        LOCAL_SHA256="$($SHA256_CMD $DESTINATION | cut -f 1 -d ' ' )"

        echo "  Checksums for $DESTINATION vs $FILE_URL"
        echo "    Local:"
        echo "      md5sum: $LOCAL_MD5"
        echo "      sha1:   $LOCAL_SHA1"
        echo "      sha256: $LOCAL_SHA256"
        echo "    Remote:"
        echo "      md5sum: $REMOTE_MD5"
        echo "      sha1:   $REMOTE_SHA1"
        echo "      sha256: $REMOTE_SHA256"

        if [ "$REMOTE_MD5" != "$LOCAL_MD5" ] || [ "$REMOTE_SHA1" != "$LOCAL_SHA1" ] || [ "$REMOTE_SHA256" != "$LOCAL_SHA256" ]; then
            echo -e "    ${RED}Checksums do not match $FILE${NC}"
            rm $DESTINATION
        else
            echo -e "    ${GREEN}Checksums match for $FILE${NC}"
            return 0
        fi
    fi
    return 1
}

download_files() {

    # Args:
    # 1: Files to download, space separated, as one string.
    # 2: Destination on local file system, can be relative path or full path.

    FILES="$1"
    if [ -z "$FILES" ]; then
        echo "No files specified to download. Exiting..."
        exit 1
    fi

    FINAL_DESTINATION="$2"
    if [ -z "$FINAL_DESTINATION" ]; then
        echo "No destination specified to download. Exiting..."
        exit 1
    fi
    
    REMOTE_BASE_URL="https://$ARTIFACTORY_HOSTNAME/artifactory"
    ARTIFACTORY_BASE_API="https://$ARTIFACTORY_HOSTNAME/artifactory/api/storage"

    mkdir -p $FINAL_DESTINATION

    for FILE in $FILES;
    do
        echo "$FILE:"
        FILE_URL="$REMOTE_BASE_URL/$FILE"
        CHECKSUMS=$($CURL_CMD -s "$ARTIFACTORY_BASE_API/$FILE" | jq '.checksums')
        if [ "$CHECKSUMS" == "null" ]; then
            echo "$FILE_URL does not exist. Artifactory API call to $ARTIFACTORY_BASE_API/$FILE failed"
            exit 1
        fi

        DESTINATION="$FINAL_DESTINATION/$(basename $FILE)"
        if ! checksums "$DESTINATION" "$CHECKSUMS" "$FILE_URL"; then
            $CURL_CMD "$FILE_URL" -o "$DESTINATION"
            if ! checksums "$DESTINATION" "$CHECKSUMS" "$FILE_URL"; then
                echo "Failed to download $FILE from $FILE_URL to $DESTINATION"
                exit 1
            fi
        fi
    done
}