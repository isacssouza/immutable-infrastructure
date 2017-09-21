#!/usr/bin/env bash

set -ex

cd ${WORKSPACE}/packer
packer build -only amazon-ebs -var jar_path=api-0.0.1-SNAPSHOT.jar api.json | tee packer-out.txt
grep 'amazon-ebs: AMI: ami-' packer-out.txt \
    | grep -o 'ami-.*$' \
    > ami-id.txt