#!/bin/sh

function init_var {
    if [ ${INITVAR:-0} == '0' ]; then
        # Only initialize those variable once

        # Make sure we run this script from the py_bots/tests directory
        SCRIPT_NAME=$(basename $0)
        if [ ! -f $SCRIPT_NAME ]; then
            echo "please run this script ($SCRIPT_NAME) from the py bots test directory"
            exit
        fi

        # Get the base directory for the IFX repository
        HOME_POLYSIGN=$(pwd | sed 's/\/bots\/py_bots\/tests//')

        HOME_K8="$HOME_POLYSIGN/rippled"
        HOME_ROBOT="$HOME_K8/bots/py_bots/tests"
        HOME_LOGS="$HOME_ROBOT/logs"

        IP_ADDRESS=`minikube ip` # Get IP Address of the minikube
        WAITSEC=20
    fi

    RIPPLED_PORT=30006
    RIPPLED_VERSION="0.80.0"
}

####
# Save the logs
function save_logs {
    if [ ! -d $HOME_LOGS ]; then
        mkdir $HOME_LOGS
    fi

    LOGDIR=${HOME_LOGS}/$(date "+%Y-%m-%d_%Hh_%Mm_%Ss")
    if [ ! -d $LOGDIR ]; then
        mkdir $LOGDIR
    fi

    echo "Copy logs in directory $LOGDIR"

    # Move all logs
    cd $HOME_ROBOT
    for FILE in log.html output.xml report.html; do
        if [ -f $FILE ]; then
            mv $FILE $LOGDIR
        fi
    done
}

#### BEGIN ####
init_var
robot   --variable HOST:$IP_ADDRESS \
        --variable RIPPLED_PORT:$RIPPLED_PORT \
        --variable RIPPLED_VERSION:$RIPPLED_VERSION \
        tests.robot
#save_logs
