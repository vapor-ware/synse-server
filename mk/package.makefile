# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Synse
#
# Recipes for packaging Synse
# ------------------------------------------------------------------------


FPM_OPTS := -s dir -n synse-server -v $(PKG_VER) \
	--architecture native \
	--url "https://github.com/vapor-ware/synse-server" \
	--license GPL2 \
	--description "IoT sensor management and telemetry system" \
	--maintainer "Thomas Rampelberg <thomasr@vapor.io>" \
	--vendor "Vapor IO" \
	--config-files lib/systemd/system/synse-server.service \
	--after-install synse-server.systemd.postinst


# Build
# -------------------------------------

# FPM is used to generate the actual packages.
# FIXME: The version is hardcoded right now, should be dynamic.
build-fpm:
	docker build -f dockerfile/fpm.dockerfile \
		-t vaporio/fpm:latest \
		-t vaporio/fpm:1.8.1 .

# hub is used to create the release in github and upload it.
# FIXME: The version is hardcoded right now, should be dynamic.
build-hub:
	docker build -f dockerfile/hub.dockerfile \
		-t vaporio/hub:latest \
		-t vaporio/hub:2.3.0-pre9 .

# packagecloud is used to upload the packages to repos
# FIXME: The version is hardcoded right now, should be dynamic.
build-packagecloud:
	docker build -f dockerfile/packagecloud.dockerfile \
		-t vaporio/packagecloud:latest \
		-t vaporio/packagecloud:0.2.42 .


# Packages
# -------------------------------------

pkg-ubuntu1604: build-fpm  ## Package Synse Server for Ubuntu 16.04
	docker run -it -v $(PWD)/packages:/data vaporio/fpm \
	-t deb \
	--iteration ubuntu1604 \
	--depends "docker-ce > 17" \
	$(FPM_OPTS) .

pkg-deb: pkg-ubuntu1604  ## Package Synse Server for Debian

pkg-el7: build-fpm  ## Package Synse Server for EL7
	docker run -it -v $(PWD)/packages:/data vaporio/fpm \
	-t rpm \
	--iteration el7 \
	--depends "docker-engine > 17" \
	$(FPM_OPTS) .

pkg-rpm: el7  ## Package Synse Server for RPM


pkg: pkg-deb pkg-rpm  ## Package Synse Server

# Release
# -------------------------------------

release-github: pkg-rpm pkg-deb  ## Create a new GitHub release for Synse Server
	docker run -it -v $(PWD):/data vaporio/hub \
		release create -d \
		-a packages/synse-server-$(PKG_VER)*rpm \
		-a packages/synse-server_$(PKG_VER)*deb \
		-m "v$(PKG_VER)" v$(PKG_VER)

release-packagecloud: pkg-rpm pkg-deb  ## Create a new PackageCloud release for Synse Server
	docker run -it -v $(PWD):/data vaporio/packagecloud \
		push VaporIO/synse/el/7 /data/$(shell ls packages/*.rpm)
	docker run -it -v $(PWD):/data vaporio/packagecloud \
		push VaporIO/synse/ubuntu/xenial /data/$(shell ls packages/*.deb)

release: release-github release-packagecloud  ## Create a new release for Synse Server