# ----------------------------------------------------------------------------
# Makefile for powercounter
#
# Copyright (c) 2024 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/powercounter)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
#  SETTINGS
# ----------------------------------------------------------------------------
APP_NAME               := powercounter
APP_VERSION            := 1.0.0

ALL_TARGET             := check-style.venv
SCRIPT                 := src/powercounter
SRC_DIRS               := $(wildcard src/. test/functional_tests/. test/unittests/.)

MAKE4PY_DOCKER_IMAGE   := make4py-powercounter
UBUNTU_DIST_VERSIONS   := 20.04 22.04 24.04
ENABLE_WINDOWS_SUPPORT := 0


# ----------------------------------------------------------------------------
#  MAKE4PY INTEGRATION
# ----------------------------------------------------------------------------
include .make4py/make4py.mk


# ----------------------------------------------------------------------------
#  OWN TARGETS
# ----------------------------------------------------------------------------
ifeq ($(ON_WINDOWS),0)

.PHONY: system-setup-prod pip-install-prod build-docker

pip-install-prod:
	@echo "-------------------------------------------------------------"
	@echo "Installing package requirements (production)..."
	@echo "-------------------------------------------------------------"
	@pip install -r pip_deps/requirements-linux-py3.12.2.txt

system-setup-prod: pip-setup pip-install-prod pip-upgrade-stuff

build-docker:
	@docker build -t $(APP_NAME):$(APP_VERSION) --build-arg PYTHON_VERSION=3.12 .

run-docker:
	@docker run -d --restart=always --name=$(APP_NAME) \
	  -v /dev:/dev -v /run/udev:/run/udev:ro \
	  --device-cgroup-rule='c 188:* rmw' \
	  $(APP_NAME):$(APP_VERSION) \
	  -v print

ifneq ($(FUNCTEST_DIR),)

ifeq ($(SWITCH_TO_VENV),1)

test-docker: test-docker.venv

else

test-docker:
	@echo "Testing docker image $(APP_NAME):$(APP_VERSION)..."
	@pytest --executable "docker run --rm -v$(CURDIR):$(CURDIR):ro --entrypoint /powercounter/src/powercounter $(APP_NAME):$(APP_VERSION)" $(FUNCTEST_DIR)
	@echo "Docker image $(APP_NAME):$(APP_VERSION) tested successfully."

endif
endif
endif


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
