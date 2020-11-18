#!/bin/bash -e
#
# Build powercounter on Ubuntu 16.04, 18.04 and 20.04
#

apt-get update
apt-get -y dist-upgrade

apt-get -y install lsb-release make python3-dev python3-venv binutils

ln -sf bash /bin/sh

cd /workdir
make clean
make unittests.venv
make pyinstaller.venv
make pyinstaller-test

mv dist/powercounter releases/powercounter_$(lsb_release -i -s)$(lsb_release -r -s)_amd64
chown $TGTUID:$TGTGID releases/powercounter_$(lsb_release -i -s)$(lsb_release -r -s)_amd64

make clean
