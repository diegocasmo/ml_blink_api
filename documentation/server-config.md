# Server Configuration

This guide explains how to configure an Ubuntu 16.04.5 server to serve the `ml_blink_api` Flask application. It assumes Ubuntu 16.04.5 is already installed, SSH is available on it, and the machine has been assigned a Floating IP address. If you get stuck, these are some helpful resources:
  - [How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)

### Install Apache
  - Run the following commands to install the Apache web server
``` bash
sudo apt-get update
sudo apt-get install apache2
```
  - Verify Apache is correctly installed by visiting the server's Floating IP address. If everything went smoothly, you should see the default Ubuntu Apache web page.
``` bash
http://<Floating IP>
```

### Install and Enable `mod_wsgi`
  - WSGI (Web Server Gateway Interface) is an interface between web servers and web applications for python. `Mod_wsgi` is an Apache HTTP server mod that enables Apache to serve Flask applications.
``` bash
sudo apt-get install libapache2-mod-wsgi python-dev
```
  - Enable `mod_wsgi`
```
sudo a2enmod wsgi
```

### Create Directory Structure
  - Run the  following commands to create the required directory structure in `/var/www`:
```
cd /var/www 
sudo mkdir ml_blink_api
cd ml_blink_api
sudo mkdir ml_blink_api
cd ml_blink_api
```
  - The file structure should now look like this (you can visualize it by running the command `tree` in `/var/www` - if not installed, run the command `sudo apt-get install tree`):
```
├── html
│   └── index.html
└── ml_blink_api
    └── ml_blink_api
```
  - Create a sample Flask application in `/var/www/ml_blink_api/ml_blink_api` by running the following command
```
sudo vi __init__.py
```
  - Add following logic to the file:
``` python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World"

if __name__ == "__main__":
    app.run()
```

### Install Flask and Dependencies
  - Install `pip`
``` bash
sudo apt-get update
sudo apt-get install python-pip
```
  -  Install `flask`
``` bash
sudo pip install Flask
```

### Configure and Enable a New Virtual Host
  - Issue the following command in your terminal:
```bash
sudo vi /etc/apache2/sites-available/ml_blink_api.conf
```
  - Add the following lines of code to the file to configure the virtual host (replace `<Floating IP>` with the server's actual Floating IP address, and the ServerAdmin with your email)
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

### Create the `.wsgi` File
  - Apache uses the `.wsgi` file to serve the Flask app. Move to the `/var/www/ml_blink_api` directory and create a file named `ml_blink_api.wsgi` with following commands:
``` bash
cd /var/www/ml_blink_api
sudo vi ml_blink_api.wsgi 
```
  - Add the following lines of code to the `ml_blink_api.wsgi` file:
``` bash
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/ml_blink_api/")

from ml_blink_api import app as application
```

### Restart Apache
  - Restart apache by running the following command:
``` bash
sudo service apache2 restart
```
  - You have successfully deployed a flask application! You should be able to access it at `http://<Floating IP>`
