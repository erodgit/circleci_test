#!/bin/sh

# This script will stop all docker processes for the ripple-soltuion
# Version 1.0
# First implementation

# Functions returning the docker icontainer ID
function container_id_match() {
    # $1 should have a name to match
    if [ ! $1 ]; then
        echo 'NONE'
        return 0
    fi
    # Pattern matching to find the line matching, then capturing the container id
    local container_id=$(docker ps|awk "/$1/ {print \$1}")
    echo ${container_id:='NONE'}
}

# Function stopping and removing the contaner id
function stop_rm_container() {
    if [ $# = 0 ]; then
        # nothing to do, exit the function
        return 0
    fi
    # Parameters will have the container id or 'NONE'
    local list=$(container_id_match $1)
    for name in $list; do
        if [ $name == 'NONE' ]; then
            # Nothing to do
            continue
        fi
        docker stop $name
        docker rm $name
    done
}

### Main script

# Stopping and removing ripple-solution containers
echo "Removing ripple-consumer container(s)"
stop_rm_container 'ripple-consumer'

echo "Removing ripple-provider container(s)"
stop_rm_container 'ripple-provider'

