#!/bin/sh

# Setup the docker private registry secret for K8
REG_LOGIN="inzbox"
REG_PASSWORD="xxx"
REG_EMAIL="erodriguez@polysin.io"

DOCKER_SERVER="https://index.docker.io/v1/"
NAME_SECRET="regsecret"

# check the current secret
kubectl get secret | grep "$NAME_SECRET" 2>&1 >/dev/null
if [ $? == "0" ];then
    echo "secret \"$NAME_SECRET\" already exist"
    echo "To remove $NAME_SECRET run this command:"
    echo "> kubectl delete secret $NAME_SECRET"
    exit
fi

kubectl create secret docker-registry "$NAME_SECRET" \
        --docker-server="$DOCKER_SERVER" \
        --docker-username="$REG_LOGIN" \
        --docker-password="$REG_PASSWORD" \
        --docker-email="$REG_EMAIL"


