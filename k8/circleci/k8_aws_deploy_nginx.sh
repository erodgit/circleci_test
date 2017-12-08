#!/bin/sh

if [ "$1" == "delete" ]; then
    echo "** Stopping services for nginxcontent"
    COMMAND=delete
else
    echo "** Starting services for nginxcontent"
    COMMAND=apply
fi

# Service to add rippled port
kubectl $COMMAND -f k8_nginx_service.yml

# Start consumer pod
kubectl $COMMAND -f k8_nginx_pod.yml
