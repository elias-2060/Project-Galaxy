#!/bin/bash

# install sudo permissions to restart service
install -m 440 -D /opt/project-galaxy/code/server/sudoers.d/project-galaxyd /etc/sudoers.d/

# install managment server environment file
mkdir -p /etc/project-galaxy/management
install -m 600 -D /opt/project-galaxy/code/management/env_settings /etc/project-galaxy/management/
echo -e "\e[31m!! Do not forget to add an AUTH_TOKEN in /etc/project-galaxy/management/env_settings else the management server will run with the empty string as token !!\e[0m"

# install management service
install -m 755 -D /opt/project-galaxy/code/management/project-galaxy-management.service /etc/systemd/system/

# install web service
install -m 755 -D /opt/project-galaxy/code/server/project-galaxyd.service /etc/systemd/system/

# create nginx config directory
mkdir -p /opt/project-galaxy/code/server/nginx-config
chown project-galaxy:www-data /opt/project-galaxy/code/server/nginx-config/

# install nginx configuration
install -m 644 -D /opt/project-galaxy/code/server/project-galaxyd.conf /opt/project-galaxy/code/server/nginx-config/

# add site to nginx
install -m 644 -D /opt/project-galaxy/code/server/incl-project-galaxy.conf /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/incl-project-galaxy.conf /etc/nginx/sites-enabled/

# create python virtual environment
python3 -m venv /opt/project-galaxy/code/.venv
/opt/project-galaxy/code/.venv/bin/pip install -r /opt/project-galaxy/code/requirements.txt
chown -R project-galaxy:www-data /opt/project-galaxy/code/.venv

# create default .env.production file for vite if it doesn't exist
if [ ! -f /opt/project-galaxy/code/frontend/project-galaxy-front/.env.production ]; then
    echo "VITE_API_URL=https://team5.ua-ppdb.me/api" > /opt/project-galaxy/code/frontend/project-galaxy-front/.env.production
fi


