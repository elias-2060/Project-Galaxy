# Backend

This file contains information about the backend of [Project Galaxy](../README.md).


## How to run the app locally (on PyCharm if wanted): ###

If you want to use PyCharm, please use **Unix** or atleast have the **Unix terminal** in PyCharm so that you can install all the packages.
If you don't use Unix, you are forced to install all packages manually. The packages and respective versions are found in [`requirements.txt`](./requirements.txt)

For Unix users: All the commands should be entered in the PyCharm Linux terminal.

#### 1. Postgres database and Python interface
```bash
sudo apt install postgresql python3-psycopg2
```


#### 2. Create the database
First configure the database with `postgres` user:
```bash
sudo su postgres
psql
```
Then create a role 'app' that will create the database and be used by the application, and drop the old database if it exists:
```sql
CREATE ROLE app WITH LOGIN CREATEDB;
DROP DATABASE IF EXISTS db_proj_galaxy;
CREATE DATABASE db_proj_galaxy OWNER app;
```
Now set the password to **1234**
```sql
\password app
```
And enter **1234**.

You need to 'trust' the role to be able to login. Add the following line to `/etc/postgresql/15/main/pg_hba.conf` (you need root access, version may vary). __It needs to be the first rule (above local all all peer)__.
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# app
local   db_proj_galaxy  app                                     trust
```
and restart the service. Then initialize the database:
```bash
sudo systemctl restart postgresql
```

### 3. Virtual environment

First we are going to make a virtual python environment for our program.
```bash
virtualenv -p python3 .venv
source .venv/bin/activate
```


### 4. Install all the required libraries

```bash
pip3 install -r requirements.txt
```


### 5. Run the app

#### 5.1 Through (normal) PyCharm

If you want to use PyCharm normally, you can just run [`app.py`](./app.py) and everything should work fine.
If you are missing libraries, check if you are using the Python Interpreter in the [`/.venv/`](./.venv) folder or if you installed all the required packages correctly.


#### 5.2 Through the Terminal
If you want to run it through the Terminal use this command when you are in the /backend/ folder:
```bash
python3 app.py
```


#### 5.3 Viewing the app

The game (provided it has been exported exported) will be served on http://localhost:8080.  
For demonstration purposes the api endpoints at http://localhost:8080/api/time, http://localhost:8080/api/point/x and http://localhost:8080/api/point/y also exist. 


### 6 Customizing the server
If you want the server to run on a different address, port or in debug mode you can set the following enviroment variables.

- `ADDR`: set this variable to the address you want the server to listen to.
- `PORT`: set this variable to the port number you want the server to listen on.
- `DEBUG`: if this variable exists the server will run in debug mode