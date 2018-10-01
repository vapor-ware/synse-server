#!/usr/bin/env bash

# build.sh
#
# Build the Synse Server docker images (slim and full) with the
# appropriate tags.
#
# This script is intended to be called via the project Makefile
# or CI workflow where the environment variables are managed.
#

red="\033[0;31m"
green="\033[0;32m"
nc="\033[0m"

if [ ! "${IMAGE_NAME}" ]; then
    echo -e "${red}error: no image name specified for build${nc}"
    exit 1
fi

if [ ! "${IMAGE_TAGS}" ]; then
    echo -e "${red}error: no image tags specified for build${nc}"
    exit 1
fi

image="${IMAGE_NAME}"
tags="${IMAGE_TAGS}"
version=$(python -c "import synse ; print(synse.__version__)")
build_date=$(date -u +%Y-%m-%dT%T 2> /dev/null)
git_commit=$(git rev-parse --short HEAD 2> /dev/null || true)

echo "+ Building Synse Server Images +"
echo "--------------------------------"
echo " image:   ${image}"
echo " version: ${version}"
echo " tags:    ${tags}"
echo " date:    ${build_date}"
echo " commit:  ${git_commit}"
echo "--------------------------------"


for tag in ${tags}; do
    echo -e "${green}tag: ${image}:${tag}[-slim]${nc}"

    # build the SLIM version of the tag
    docker build -f dockerfile/synse.dockerfile \
        --build-arg BUILD_DATE=${build_date} \
		--build-arg BUILD_VERSION=${version} \
		--build-arg VCS_REF=${git_commit} \
		--target=slim \
		-t "${image}:${tag}-slim" .

    # build the FULL verison of the tag
    docker build -f dockerfile/synse.dockerfile \
        --build-arg BUILD_DATE=${build_date} \
		--build-arg BUILD_VERSION=${version} \
		--build-arg VCS_REF=${git_commit} \
		-t "${image}:${tag}" .
done
