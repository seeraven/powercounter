#!/bin/bash
#
# Entry point script for powercounter docker image
#

THIS_DIR=$(dirname $(readlink -f $0))

while `true`; do
    echo "$(date +'%Y-%m-%d %T') [WRAPPER]: Starting powercounter with arguments $@:"
    ${THIS_DIR}/powercounter "$@"
    RETCODE=$?
    echo "$(date +'%Y-%m-%d %T') [WRAPPER]: Powercounter exited with return code $RETCODE."
    if [ $RETCODE == 0 ]; then
        exit 0
    fi
    echo
    echo "$(date +'%Y-%m-%d %T') [WRAPPER]: Restarting in 30 seconds..."
    sleep 30s
    echo
    echo
    echo
done
