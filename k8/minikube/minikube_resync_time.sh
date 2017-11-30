#!/bin/sh

# Minikube get timelag when the MacBook go to sleeping mode
# This script allows to resync the time used by minikube

echo "Resyncing the time on the minikube"
minikube ssh -- docker run -i --rm --privileged --pid=host debian nsenter -t 1 -m -u -n -i date -u $(date -u +%m%d%H%M%Y)

