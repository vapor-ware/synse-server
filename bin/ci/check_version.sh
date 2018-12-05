#!/usr/bin/env bash

# Defined in project - see Makefile
pkg_version="${PKG_VERSION}"

# Defined on Jenkins CI server for tag being built
tag_version="${TAG_NAME}"

# Note the 'v' prefix on the version. We expect the tag to start
# with 'v', e.g. v1.2.3, but the version aas defined by synse.__version__
# does not have the 'v' prefix, so we add it here when checking.

if [ ! "${pkg_version}" ] && [ ! "${tag_version}" ]; then
    echo "No version or tag specified."
    exit 1
fi

if [ "v${pkg_version}" != "${tag_version}" ]; then
    echo "Versions do not match: pkg@${pkg_version} tag@${tag_version}"
    exit 1
fi

echo "Versions match: pkg@${pkg_version} tag@${tag_version}"