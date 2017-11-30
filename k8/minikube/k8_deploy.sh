#!/bin/sh

if [ "$1" == "delete" ]; then
    echo "** Stopping services"
    COMMAND=delete
else
    echo "** Starting services"
    COMMAND=apply
fi

# Make sure the minikube environment exist
./minikube_test.sh
if [ "$?" != 0 ]; then
    echo "Error: Minikube environment is not ready"
    echo "Exiting $0"

    # Display minikube status
    echo
    echo "minikube status:"
    /usr/local/bin/minikube status
    exit 1
fi

if [ "$COMMAND" == "apply" ]; then
    # Get OS name
    MYOS=$(uname)
    if [ ${MYOS:="0"} == "Darwin" ]; then
        # Minikube get time lag when the Macbook goes to sleep
        # Resync the time with the minikube
        ./minikube_resync_time.sh 2>/dev/null
    fi
fi

# Setup the environment for the minikube
eval $(minikube docker-env)

# Service to add rippled port
kubectl $COMMAND -f k8_nginx_service.yml

# Start consumer pod
kubectl $COMMAND -f k8_nginx_pod.yml
