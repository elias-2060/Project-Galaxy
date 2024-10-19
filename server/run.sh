#!/bin/bash
/opt/project-galaxy/code/.venv/bin/gunicorn --workers 3 --bind unix:server/project-galaxy.sock -m 007 app:app