#!/bin/sh

# IP Address to reach rippled in K8 AWS
IP_AWS_RIPPLED="18.216.216.236"
PORT=30006
RIPPLED_VERSION="0.80.0"

# Run robot tests
robot --variable HOST:$IP_AWS_RIPPLED \
        --variable RIPPLED_PORT:$PORT \
        --variable RIPPLED_VERSION:$RIPPLED_VERSION \
        tests.robot
