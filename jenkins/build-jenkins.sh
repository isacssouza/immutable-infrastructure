#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

image=${1:-immutable-infrastructure/jenkins}

docker build -t ${image} ${DIR}
