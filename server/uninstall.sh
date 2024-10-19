#!/bin/bash

# remove nginx configuration
rm /etc/nginx/sites-enabled/incl-project-galaxy.conf /etc/nginx/sites-available/incl-project-galaxy.conf

# restart nginx to use new configuration
systemctl restart nginx

# disable and stop web and management services
systemctl disable project-galaxyd.service project-galaxy-management.service --now

# remove web and management service files
rm /etc/systemd/system/project-galaxyd.service /etc/systemd/system/project-galaxy-management.service

# remove management service
rm -r /opt/project-galaxy /etc/project-galaxy

# delete project-galaxy user
userdel project-galaxy