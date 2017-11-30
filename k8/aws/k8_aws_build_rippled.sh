#!/bin/bash

image_name="rippled"
container_name=$image_name

# Setup the environment for the minikube
docker build -t polysignorg/rippled ../..

# Push image to repository
docker push polysignorg/rippled
