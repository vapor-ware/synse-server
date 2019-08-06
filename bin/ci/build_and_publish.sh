#!/usr/bin/env bash
#
# build_and_publish.sh
#
# This script is used during CI to build and push images to DockerHub.
# This is run from the projects root directory, e.g. './bin/ci/build_and_publish.sh'
# so all paths should be relative to the repo root.
#
# The CI environment should provide the following environment variables:
#   IMAGE_NAME: The name of the Docker image (without tags)
#   CIRCLE_TAG: The name of the git tag
#
# All arguments passed to the script should be tags for the $IMAGE_NAME.
# If $CIRCLE_TAG exists, it will be parsed to generate the tags for all
# appropriate versions. For example:
#   CIRCLE_TAG  ->  IMAGE TAGS
#   1           ->  1
#   1.2         ->  1, 1.2
#   1.2.3       ->  1, 1.2, 1.2.3
#

echo "Building and Publishing Images"

#
# Get Tags
#
# In this section, we collect all of the tags that we will use for
# the image to be built and pushed.
#

declare -a tags

if [[ "${TAG_NAME}" ]]; then
    echo "Found TAG_NAME: ${TAG_NAME}"

    # First, search for "-" in the tag. This would be the case for tags
    # with suffixes, e.g. "1-dev", "1.2.3-rc0". If a suffix is present,
    # then we will not generate version component tags; we will just use
    # the full tag.
    suffix_count=$(awk -F- '{print NF-1}' <<< "${TAG_NAME}")
    if [[ ${suffix_count} -eq 0 ]]; then
        IFS='.' read -r -a array <<< "${TAG_NAME}"

        major="${array[0]}"
        minor="${array[1]}"
        micro="${array[2]}"

        if [[ "${micro}" ]]; then
            tags+=("${major}.${minor}.${micro}")
        fi
        if [[ "${minor}" ]]; then
            tags+=("${major}.${minor}")
        fi
        if [[ "${major}" ]]; then
            tags+=("${major}")
        fi
    else
        tags+=("${TAG_NAME}")
    fi

    if [[ "${tags}" ]]; then
        echo "Created image tags from TAG_NAME: ${tags[@]}"
    else
        echo "No image tags created from TAG_NAME"
    fi

    # Add the TAG_NAME to the tags. In some cases, this may duplicate
    # a tag, but building with the same tag should just use the cache
    # and not cause any problems.
    tags+=("${TAG_NAME}")
fi


# Now, add all of the tags provided via command line arguments
for arg in "$@"; do
    tags+=("$arg")
done

echo "All tags for ${IMAGE_NAME}: ${tags[@]}"


#
# Build
#
# Now, we build the image and tag it with the tags we collected above.
# How the image is built is up to the repo. Here, we leverage the Makefile
# build logic which will build both the 'release' and 'slim' images for
# the given tags.
#
# This script must be run from the repo root for this to work, since it
# uses a Make target defined there.
#

echo "Building Image"

# First make the docker image based on the Makefile -- this will tag as :latest
make docker

echo "Generating Image Tags"

# Generate the desired tags off of the built latest image
for tag in "${tags[@]}"; do
    echo "  tag: ${tag}"
    docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${tag}
done

#
# Publish
#
# Now, we publish the images to DockerHub.
#
# Since we built the images from the Makefile, we do not have a complete
# list of all tags for the image that we tagged (e.g. especially since some
# have the added -slim suffix.
#

echo "Pushing Images"

# For all tags, push the base tag and the slim tag. These should have been
# built in previous steps and therefore should exist at this point.
for tag in "${tags[@]}"; do
    docker push ${IMAGE_NAME}:${tag}
done
