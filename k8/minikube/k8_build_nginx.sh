#!/bin/bash

image_name="ngixcontent"
container_name=$image_name

# Setup the environment for the minikube
eval $(minikube docker-env)

# Dockerfile is 2 directory up
docker build -t $image_name ../..
