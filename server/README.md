# Server configuration

## Installing libraries

Install nginx, go, python3.10 - python3.12, postgresql, npm

[Set up the database.](../database/doc/Interacting%20with%20the%20Database.md)

## Installing the server

### Creating the user
Create a new project-galaxy user.
```bash
sudo useradd project-galaxy -c "Project Galaxy server user" -g www-data -d /opt/project-galaxy -m -r
```


### Creating a deployment key

```bash
sudo su project-galaxy
ssh-keygen -t rsa # name the key /opt/project-galaxy/.ssh/deployment , without a password
eval $(ssh-agent -s)
ssh-add /opt/project-galaxy/.ssh/deployment
exit
```
Add `deployment.pub` to repository with read access.


### Clone the project

As the project-galaxy user:
```bash
git clone "git-repo-url" /opt/project-galaxy/code
```

### Switch to the production branch
As the project-galaxy user:
```bash
cd ~/code
git checkout production
```

### Run the install script
```bash
/opt/project-galaxy/code/server/install.sh
```

### Enabling the management server
```bash
systemctl enable project-galaxy-management.service --now
```

### Configuring the server

#### /etc/project-galaxy/management/env_settings


## Updating the server
git pull duh




## File locations

### Server files
Server files will be installed to `/opt/project-galaxy`
`nginx-config`: Created by the install script. Contains the nginx configuration. If the server is disabled the .conf file is renamed to .conf.disabled and will no longer be included by nginx


## Management server
### Configuring the management server
### Starting the management server


## Uninstalling

### Manually
1. Remove nginx config: `rm /etc/nginx/sites-enabled/incl-project-galaxy.conf /etc/nginx/sites-available/incl-project-galaxy.conf`
2. Restart nginx: `sudo systemctl restart nginx`
3. Disable services: `sudo systemctl disable project-galaxyd.service project-galaxy-management.service --now`
4. Remove service files: `rm /etc/systemd/system/project-galaxyd.service /etc/systemd/system/project-galaxy-management.service`
5. Remove server files: `rm -r /opt/project-galaxy /etc/project-galaxy`
6. Remove user: `sudo userdel project-galaxy`

### Automated
The server comes with an uninstall script that does all the cleanup steps above. The script can be run with `sudo /opt/project-galaxy/code/server/uninstall.sh`.