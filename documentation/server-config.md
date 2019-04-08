# Server Configuration

This guide explains how to configure an Ubuntu 16.04 server to serve the `ml_blink_api` Flask application in the SNIC Cloud. If you get stuck, these are some helpful resources:
  - [How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
  - [Install MongoDB Community Edition on Ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)
  - [How to quickly setup MongoDB on DigitalOcean](https://medium.com/ninjaconcept/how-to-quickly-setup-mongodb-on-digitalocean-3d9791a7aaa4)
  - [How to Install MongoDB on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-16-04)
  - [How To Install and Configure Redis on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04)
  - [How to Set Up a Task Queue with Celery and RabbitMQ](https://www.linode.com/docs/development/python/task-queue-celery-rabbitmq/)

### Access & Security Configuration
  - Go to `Compute > Access & Security` and click in `Create Security Group`
  - Name the new security group `ml_blink_api`
  - Once created, add the following rules with their default values to it: `HTTP`, and `HTTPS`

### Launch Instance
  - Go to `Compute > Instance` and click in `Launch Instance`
  - These are the only options that need to be changed, all others stay with their defaults:
    - Name the new instance `ml_blink_api` in the `Details` tab
    - In the `Source` tab, select the option `Image` as the `Boot Source` and find the Ubuntu 16.04 image
    - Select `ssc.xlarge` in the `Flavor` tab
    - Select `IPv4` in the `Networks` tab
    - Select `ml_blink_api` in the `Security Groups` tab
    - Create a key pair in the `Key Pair` tab. Save it in your machine in a save place
  - Click on `Launch Instance`
  - Once created, associate a Floating IP address to it

### SSH Into the Instance
  - In your machine, change the permissions of the `.pem` key pair file (replacing `<file_name>` with the name of the file)
```
chmod 400 <file_name>.pem
```
  - SSH into the machine (replace `<file_name>`, and `<Floating IP>` with their values)
``` bash
ssh -i <file_name>.pem ubuntu@<Floating IP>
```

### Install Apache
  - Run the following commands to install the Apache web server
``` bash
sudo apt-get update
sudo apt-get install -y apache2
```
  - Verify Apache is correctly installed by visiting the server's Floating IP address. If everything went smoothly, you should see the default Ubuntu Apache web page.
``` bash
http://<Floating IP>
```

### Install and Enable `mod_wsgi`
  - WSGI (Web Server Gateway Interface) is an interface between web servers and web applications for python. `Mod_wsgi` is an Apache HTTP server mod that enables Apache to serve Flask applications.
``` bash
sudo apt-get install -y libapache2-mod-wsgi-py3 python-dev
```
  - Enable `mod_wsgi`
```
sudo a2enmod wsgi
```

### Configure and Enable a New Virtual Host
  - Issue the following command in your terminal:
```bash
sudo vi /etc/apache2/sites-available/ml_blink_api.conf
```
  - Add the following lines of code to the file to configure the virtual host (replace `<Floating IP>` with the server's actual Floating IP address, and the ServerAdmin with your email). Notice the `/` at the end of the Floating IP address is not included!
```
<VirtualHost *:80>
    ServerName http://<Floating IP>
    ServerAdmin <admin@foo.bar>
    WSGIScriptAlias / /var/www/ml_blink_api/ml_blink_api.wsgi
    <Directory /var/www/ml_blink_api/ml_blink_api/>
      Order allow,deny
      Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```  
  - Enable the virtual host with the following command 
``` bash
sudo a2ensite ml_blink_api
```
  - Reload Apache to activate the new configuration by running
``` bash
sudo service apache2 reload
```

### Install MongoDB
  - [Follow steps 1 through 4 to install MongoDB](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/#import-the-public-key-used-by-the-package-management-system)
  - Next, start MongoDB with `systemctl`
``` bash
sudo systemctl start mongod
```
  - You can also use `systemctl` to check that the service has started properly
``` bash
sudo systemctl status mongod
```
  - The last step is to enable automatically starting MongoDB when the system starts
``` bash
sudo systemctl enable mongod
```

### Enable MongoDB Authorization
  - Enter the MongoDB shell and connect to the admin database
``` bash
mongo
use admin
```
  - Create an admin user (replace `<user>` and `<pwd>` with the corresponding values you desire to use)
``` bash
db.createUser(
  {
    user: "<user>",
    pwd: "<pwd>",
    roles: ["root"]
  }
)
```
  - Exit the MongoDB shell by typing `exit` and pressing enter
  - Activate MongoDB authorization system by modifying `/etc/mongod.conf`
``` bash
sudo vi /etc/mongod.conf
```
  - Add the following lines at the end of the file
``` bash
security:
  authorization: enabled
```
  - Restart MongoDB to apply the changes
```
sudo service mongod restart
```

### Install and Configure Redis
  - [Follow this guide, step-by-step, to install and configure Redis](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-redis-on-ubuntu-16-04)

### Configure Git
  - Configure Git with your GitHub account
``` bash
git config --global user.name "<username>"
git config --global user.email "your@github.email"
```
  - Generate a new SSH key (press Enter when prompted for file to save or passphrase)
```
sudo ssh-keygen -t rsa -b 4096 -C "<your@github.email>"
```
  - Change key's file permissions
``` bash
sudo chmod 600 /root/.ssh/id_rsa.pub
```
  - Start the ssh-agent in the background
```
eval "$(ssh-agent -s)"
```
  - Add your SSH private key to the ssh-agent
```
sudo ssh-add -k /root/.ssh/id_rsa
```
  - Add SSH key to your GitHub account
```
sudo cat /root/.ssh/id_rsa.pub
```
  - Go to `Settings > SSH and GPG keys` in GitHub, click on New SSH Key, and paste the key

### Pull Latest `ml_blink_api`
  - Run the following commands to download the repo
``` bash
cd /var/www/
sudo git clone git@github.com:diegocasmo/ml_blink_api.git
cd ml_blink_api/
sudo git pull
```
  - Install `pip3`
``` bash
sudo apt-get -y install python3-pip
```
  - Install python dependencies
``` bash
sudo pip3 install -r requirements.txt
```
  - Create the environmental variables file
```
sudo touch /var/www/ml_blink_api/.env
```
  - Fill the newly created `.env` file assigning the variables declared in `.env.example` their real values
    - The MongoDB URI follows this format: `mongodb://<user>:<pwd>@localhost:27017`
    - Set `FLASK_ENV=production`

### Restart Apache
  - Restart apache by running the following command:
``` bash
sudo service apache2 restart
```

### Configure Celery
  - Create a new service definition in `/etc/systemd/system/celeryd.service`:
``` bash
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=root
Group=root
EnvironmentFile=/etc/default/celeryd
WorkingDirectory=/var/www/ml_blink_api
ExecStart=/bin/sh -c '${CELERY_BIN} multi start ${CELERYD_NODES} \
  -A ${CELERY_APP} -B --pidfile=${CELERYD_PID_FILE} \
  --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'
ExecStop=/bin/sh -c '${CELERY_BIN} multi stopwait ${CELERYD_NODES} \
  --pidfile=${CELERYD_PID_FILE}'
ExecReload=/bin/sh -c '${CELERY_BIN} multi restart ${CELERYD_NODES} \
  -A ${CELERY_APP} -B --pidfile=${CELERYD_PID_FILE} \
  --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'

[Install]
WantedBy=multi-user.target
```
  - Create the `/etc/default/celeryd` configuration file. Note that in addition to the configuration below, you MUST manually add all the enviromental variables at the top of this file:
``` bash
#------------ Settings for ML Blink API ------------#
# Copy/paste all variables in the `/var/www/ml_blink_api/.env` file here

# Name of nodes to start
CELERYD_NODES="w1"

# Absolute or relative path to the 'celery' command:
CELERY_BIN="/usr/local/bin/celery"

# App instance to use
CELERY_APP="ml_blink_api.jobs.tasks"

# How to call manage.py
CELERYD_MULTI="multi"

# Where to chdir at start.
CELERYBEAT_CHDIR="/var/www/ml_blink_api/"

# Extra arguments to celerybeat
CELERYBEAT_OPTS="--schedule=/var/run/celery/celerybeat-schedule"

# - %n will be replaced with the first part of the nodename.
# - %I will be replaced with the current child process index
#   and is important when using the prefork pool to avoid race conditions.
CELERYD_PID_FILE="/var/run/celery/%n.pid"
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_LOG_LEVEL="INFO"
```
  - Create log and pid directories:
``` bash
sudo mkdir /var/log/celery /var/run/celery
```
  - Reload `systemctl` daemon by running `sudo systemctl daemon-reload`
  - Enable the service to startup at boot: `sudo systemctl enable celeryd`
  - Start the service `sudo systemctl start celeryd`
  - Verify the worker correctly setup by running the following commands:
    - `systemctl status celeryd.service`
    - `journalctl -xe`
    - `cat /var/log/celery/w1.log`

### Access the API
  - You have successfully deployed a flask application! You should be able to access it at `http://<Floating IP>`

### Debugging
  - If the installation doesn't work, the following commands might be helpful:
    - `tail /var/log/apache2/error.log` will show log errors by the Apache server. If accessing `http://<Floating IP>` returns an error, this command will give you a more detailed description of what happened.
