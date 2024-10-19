#!/bin/bash

cd /opt/project-galaxy/code/

# ensure only one instance of the redeployment is running
pidof -o %PPID -x $0 >/dev/null && echo "ERROR: Redeployment already running" && exit 1

# disable the server
/opt/project-galaxy/code/server/disable.sh

# get latest changes
echo "Fetching latest changes"
# git checkout production
git pull

# echo "migrating database to latest version"
# TODO migrate database once migration is added

# update all python packages
/opt/project-galaxy/code/.venv/bin/pip install -r /opt/project-galaxy/code/requirements.txt

cd /opt/project-galaxy/code/frontend/project-galaxy-front/
npm install
cd /opt/project-galaxy/code/

make frontend-build

# reenable the server
/opt/project-galaxy/code/server/enable.sh

# done
echo "Server redeployed"
