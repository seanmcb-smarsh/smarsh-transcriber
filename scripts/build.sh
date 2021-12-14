#!/usr/bin/env bash

# Set Local Language
locale-gen en_GB.UTF-8

# Upgrade pip to the latest version.
echo "Install/Update pip3"
sudo apt-get install gcc libpq-dev -y
sudo -H pip3 install --upgrade pip
sudo apt-get install python3-setuptools -y
sudo apt install python3-testresources -y

SCRIPT_DIR=$(cd `dirname $0` && pwd)
echo $SCRIPT_DIR
flag=true

echo "Package setup for delivery"
python3 setup.py sdist bdist_wheel
if [[ $? > 0 ]]
then
	echo "Project Dependencies need to be installed"
	pip3 install --upgrade -r requirements/dev.txt
	if [[ $? > 0 ]]
	then
		echo "Requirements Installation Failed, existing System Setup."
	else
		echo "Trying Package setup for delivery - Again"
		python3 setup.py sdist bdist_wheel
		if [[ $? > 0 ]]
		then
			flag=false
		fi
	fi
fi
#Creates semantic version
emit_version(){
	latest_tag=`git semver get | cut -d "-" -f 1 | cut -d "." -f 1,2,3`
	build_info=`cat vault/properties/product-version.info | cut -d "=" -f 2 |  cut -d "." -f 1,2 `
	latesttag_major_version=`echo $latest_tag | cut -d "." -f 1`
	latesttag_minor_version=`echo $latest_tag | cut -d "." -f 2`
	latesttag_patch_version=`echo $latest_tag | cut -d "." -f 3`

	build_info_major_version=`echo $build_info | cut -d "." -f 1`
	build_info_minor_version=`echo $build_info | cut -d "." -f 2`

	if [[ ( $latesttag_major_version -eq $build_info_major_version ) && ( $latesttag_minor_version -eq $build_info_minor_version ) ]] 
  then
		echo "fetch patch  and increment to patch+1"
		latesttag_patch_version=$((latesttag_patch_version+1))
		export VERSION=$latesttag_major_version"."$latesttag_minor_version"."$latesttag_patch_version
	else
		echo "fetch major and minor version from $build_info and attach patch 0"
		export VERSION=$build_info_major_version"."$build_info_minor_version".0"
	fi
    export PRODUCT_VERSION=$VERSION
}
if [ "$flag" = true ]
then
	echo "Installing the Package vault for Test"
	emit_version
	pip3 install -I --user dist/transcriber-api*py3-none-any.whl
	commit_id=`git rev-parse --short HEAD`
        echo $VERSION-$commit_id >> $base_dir/build_out/git-tag.txt
	echo "Packing Everything into a Zip"
	cd dist && zip -rq "transcriber-api-$VERSION".zip transcriber*
	if [[ $? > 0 ]]
	then
		echo "Can't pack into Zip File,  existing System Setup."
		exit
	else
		echo "Packed everything into the Zip File in /dist"
	fi
else
	echo "Can't build the wheelhouse installable package for PIP"
fi