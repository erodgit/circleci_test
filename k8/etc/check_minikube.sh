#!/bin/sh

# This script checks and install the software development requirement
# Version 2017-09-11
#   brew version 1.3.2
#   xhyve version 0.2.0
#   kubectl version 1.7.5
#   minikube version 0.22.1

minikube_version="v0.22.3"
install_minikube=0              # Init variable
brew_version="1.3.2"
xhyve_file="/usr/local/opt/docker-machine-driver-xhyve/bin/docker-machine-driver-xhyve"
xhyve_version="0.2.0"
install_xhyve=0              # Init variable
kubectl_file="/usr/local/bin/kubectl"
kubectl_version="v1.7.5"
3nstall_kubectl=0              # Init variable

# Check if  brew is installed
if [ -f /usr/local/bin/brew ]; then
    brew_v=$(brew --version | awk '/^Homebrew / {print $2}')
    echo "Brew version installed: $brew_v"
else
    echo "Cannot find brew, brew must be installed, exiting"
    exit 1
fi

echo "----"

# Check if xhyve is installed
if [[ -x $xhyve_file ]]; then
    # Get xhyve version
    xhyve_v=$(brew info xhyve | awk '/^xhyve:/ {print $3}')
    echo "Found xhyve, running version $xhyve_v   (tested with version $xhyve_version)"
else
    echo "xhyve lightweight macOS virtualization solution is not found"
    echo "Do you want to install xhyve?"
    read -p "[y/N]> " answer

    if [[ ${answer:='N'} =~ ^[Yy]([eE][sS]){0,1}$ ]];then
        # Answer is yes
        install_xhyve=1
    fi
fi

if [ $install_xhyve == 1 ]; then
    echo "Installing xhyve"
    brew install xhyve
    brew install docker-machine-driver-xhyve
    sudo chown root:wheel $(brew --prefix)/opt/docker-machine-driver-xhyve/bin/docker-machine-driver-xhyve 
    sudo chmod u+s $(brew --prefix)/opt/docker-machine-driver-xhyve/bin/docker-machine-driver-xhyve 
fi

echo "----"

# Check if kubectl is installed
if [[ -x $kubectl_file ]]; then
    # Get kubectl version
    kubectl_v=$(kubectl version | awk '/^Client/ {print}'| sed 's/.*GitVersion:"\(v[0-9]*\.[0-9]*\.[0-9]*\)".*/\1/')
    echo "Found kubectl, running version $kubectl_v   (tested with version $kubectl_version)"
else
    echo "kubectl lightweight macOS virtualization solution is not found"
    echo "Do you want to install kubectl?"
    read -p "[y/N]> " answer

    if [[ ${answer:='N'} =~ ^[Yy]([eE][sS]){0,1}$ ]];then
        # Answer is yes
        install_kubectl=1
    fi
fi

if [ $install_kubectl == 1 ]; then
    echo "Installation of kubectl:"
    brew install kubectl
fi

echo "----"

# Check the minikube version
if [ -f /usr/local/bin/minikube ]; then
    # Get the version
    minikube_v=$(minikube version|awk '/^minikube version: v[0-9]/ {print $3}')
    if [ $minikube_version == ${minikube_v:='NONE'} ]; then
        # Minikube version is matching
        echo "minikube version is $minikube_version: OK"
    else
        echo "minikube installed version is $minikube_v"
        echo "Do you want to install version $minikube_version?"
        read -p "[y/N]> " answer

        # 
        if [[ ${answer:='N'} =~ ^[Yy]([eE][sS]){0,1}$ ]];then
            # Answer is yes
            install_minikube=1

            if [[ -d ~/.minikube ]]; then
                new_dir=~/.minikube_${minikube_v:="old"}
                echo "renaming ~/minikube to $new_dir"
                if [[ -d $new_dir ]]; then
                    echo "Exiting: $new_dir already exist"
                    exit 1
                fi
            fi
            # Removing the minikube previous installation
            minikube stop
            minikube delete
            # Saving minikube configuration directory
            sudo mv ~/.minikube $new_dir
            
        fi
    fi
else
    print "minikube is not installed"
    install_minikube=1
fi

if [ $install_minikube == 1 ]; then
    echo "Installing minikube"
    curl -Lo minikube https://storage.googleapis.com/minikube/releases/${minikube_version}/minikube-darwin-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/
    if [[ $? == 0 ]]; then
        echo "Starting minikube"
        minikube start --memory=6144 --vm-driver=xhyve
    else
        echo "Exiting: installation error"
        exit 1
    fi
        
fi
