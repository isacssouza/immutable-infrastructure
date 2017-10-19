#!/usr/bin/env bash

image=${1:-jenkins}
aws_profile=${2:-default}

export AWS_PROFILE=${aws_profile}
docker run \
    -e AWS_REGION=$(aws configure get region) \
    -e AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id) \
    -e AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key) \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 8081:8080 \
    -ti ${image}
