#!/bin/bash

echo "Disabling server"

# remove from nginx
echo "Removing site from nginx"
# unlink /etc/nginx/sites-enabled/project-galaxy.conf
mv /opt/project-galaxy/code/server/nginx-config/project-galaxyd.conf /opt/project-galaxy/code/server/nginx-config/project-galaxyd.conf.disabled
sudo systemctl restart nginx

# disable and stop service
echo "Stopping service"
sudo systemctl disable project-galaxyd.service --now

echo "Server disabled"

