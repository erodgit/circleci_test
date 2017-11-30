#!/bin/sh

# Return an exit status of 0 if the minikube environment is ready
MYOUTPUT=`/usr/local/bin/minikube status 2>&1`;

# Expected output is:
#minikube: Running
#cluster: Running
#kubectl: Correctly Configured: pointing to minikube-vm at 192.168.64.8

MSTATUS=$?
#echo "Return status: $MSTATUS"
#echo $MYOUTPUT
if [ "$MSTATUS" != 0 ]; then
    exit 1;
fi

echo $MYOUTPUT | grep -q "minikube: Running"
SMINIKUBE=$?
#echo "grep minikube Running => $SMINIKUBE"
if [ "$SMINIKUBE" != 0 ]; then
    exit 1;
fi


echo $MYOUTPUT | grep -q "cluster: Running"
SCLUSTER=$?
#echo "grep cluster Running => $SCLUSTER"
if [ "$SCLUSTER" != 0 ]; then
    exit 1;
fi

