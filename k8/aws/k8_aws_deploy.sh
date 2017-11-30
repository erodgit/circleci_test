#!/bin/sh

if [ "$1" == "delete" ]; then
    echo "** Stopping services for the consumer and provider"
    COMMAND=delete
else
    echo "** Starting services for the consumer and provider"
    COMMAND=apply
fi

# Service to add rippled port
kubectl $COMMAND -f k8_rippled_service.yml

# Start consumer pod
kubectl $COMMAND -f k8_rippled_pod.yml
