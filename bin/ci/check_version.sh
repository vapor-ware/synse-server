#!/usr/bin/env bash

pkg_version="${PKG_VERSION}"
circle_tag="${CIRCLE_TAG}"

# Note the 'v' prefix on the version. We expect the tag to start
# with 'v', e.g. v1.2.3, but the version aas defined by synse.__version__
# does not have the 'v' prefix, so we add it here when checking.

if [ ! "${pkg_version}" ] && [ ! "${circle_tag}" ]; then
    echo "No version or tag specified."
    exit 1
fi

if [ "v${pkg_version}" != "${circle_tag}" ]; then
    echo "Versions do not match: pkg@${pkg_version} tag@${circle_tag}"
    exit 1
fi

echo "Versions match: pkg@${pkg_version} tag@${circle_tag}"