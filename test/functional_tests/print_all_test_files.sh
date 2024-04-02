#!/bin/bash

BIN_DIR=$(dirname $(dirname $(readlink -f $0)))/libsml-testing
EXE=$(dirname $(dirname $(dirname $(readlink -f $0))))/src/powercounter

for BIN_FILE in $BIN_DIR/*.bin; do
    echo
    echo
    echo
    echo "-------------------------------------------------------------------------------"
    echo " Start $(basename $BIN_FILE)"
    echo "-------------------------------------------------------------------------------"
    $EXE -i $BIN_FILE print
    echo "-------------------------------------------------------------------------------"
    echo " End $(basename $BIN_FILE)"
    echo "-------------------------------------------------------------------------------"
done
