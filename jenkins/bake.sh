#!/usr/bin/env bash

set -ex

cd ${WORKSPACE}/packer
packer build -only amazon-ebs -var jar_path=api-0.0.1-SNAPSHOT.jar api.json \
    | grep 'amazon-ebs: AMI: ami-' \
    | grep -o 'ami-.*$' \
    > ami-id.txt