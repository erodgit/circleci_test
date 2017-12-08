#!/bin/bash

image_name="inzbox/circleci_nginx"
container_name=$image_name

# Setup the environment for the minikube
docker build -t $container_name ../..

# Push image to repository
docker push $container_name
