#!/bin/sh

echo "NOTE: you need to \"source $0\" to set the environment"

# Setup the environment for the minikube
eval $(minikube docker-env)
