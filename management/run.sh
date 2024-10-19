#!/bin/bash
if [ -z "$AUTH_TOKEN" ]; then
    echo "No AUTH_TOKEN set. Be sure to set AUTH_TOKEN in /opt/project-galaxy/code/management/env_settings"
    exit 1
fi
/usr/bin/go run /opt/project-galaxy/code/management/src/main.go
