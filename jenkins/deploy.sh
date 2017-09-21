#!/usr/bin/env bash

set -ex

cd ${WORKSPACE}/deploy

ami_id="$(cat ami-id.txt)"

virtualenv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt

ansible-playbook -e version=${BUILD_ID} -e key_name=amazonkey -e api_ami_id=${ami_id} playbooks/deploy.yml