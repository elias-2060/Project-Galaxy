#!/bin/bash

echo "Enabling server"

# enable and start service
echo "Starting service"
sudo systemctl enable project-galaxyd.service --now

# add to nginx
echo "Adding site to nginx"
mv /opt/project-galaxy/code/server/nginx-config/project-galaxyd.conf.disabled /opt/project-galaxy/code/server/nginx-config/project-galaxyd.conf
sudo systemctl restart nginx

echo "Server enabled"

