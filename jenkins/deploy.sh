#!/usr/bin/env bash

set -ex

cd ${WORKSPACE}/deploy

ami_id="$(cat ami-id.txt)"

virtualenv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt

python deploy.py ${BUILD_ID} ${ami_id}