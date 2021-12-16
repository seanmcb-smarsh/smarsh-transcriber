ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
ifndef CI_TOOLS
$(error You must set the varaible CI_TOOLS to point to where you have checked out the build-tools)
endif
include $(CI_TOOLS)/Makefile.mk

python-transcriber-api: docker-transcriber-api-builder exec-download_english_models.sh exec-download_test_data.sh
python-transcriber-api-shell: python-transcriber-api
