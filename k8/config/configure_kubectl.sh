#!/bin/sh

# Download kubectl
# wget -q https://storage.googleapis.com/kubernetes-release/release/v1.8.3/bin/linux/amd64/kubectl

# Set variable
ENDPOINT="https://api-myfirstcluster-k8s-lo-hqulii-563284583.us-east-2.elb.amazonaws.com"
#echo $ENDPOINT

CA_CRT="./ca.crt"
if [ ! -f $CA_CRT ]; then
    echo "Error: cannot find certificate $CA_CRT"
    exit 1
fi
 
# Create cluster
./kubectl config set-cluster circleci.cluster \
  --embed-certs=true \
  --server=$ENDPOINT \
  --certificate-authority=$CA_CRT

# Create user entry
# Use global environment to pass the data (this is for CircleCI)
./kubectl config set-credentials testci \
  --password=$K8USERPASSWORD \
  --username=admin

# Create Context entry
./kubectl config set-context circleci.context \
  --cluster=circleci.cluster \
  --user=testci

# View the config
./kubectl config view
