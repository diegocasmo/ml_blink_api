# Server Configuration

This guide explains how to configure an Ubuntu 16 server to serve the `ml_blink_api` Flask application. It assumes Ubuntu 16 is already installed, SSH is available on it, and the machine has been assigned a Floating IP address. If you get stuck, these are some helpful resources:
  - [How To Deploy a Flask Application on an Ubuntu VPS](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
  - [Install MongoDB Community Edition on Ubuntu](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)
  - [How to quickly setup MongoDB on DigitalOcean](https://medium.com/ninjaconcept/how-to-quickly-setup-mongodb-on-digitalocean-3d9791a7aaa4)
  - [How to Install MongoDB on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-16-04)

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

### Download `ml_blink_api`
  - Run the following commands to download the repo
``` bash
cd /var/www/
sudo wget https://github.com/diegocasmo/ml_blink_api/archive/master.zip
```
  - Unzip it
``` bash
sudo unzip master.zip
sudo rm master.zip
```
  - Change the directory name
``` bash
sudo mv ./ml_blink_api-master/ ./ml_blink_api/
```
  - Install `pip3`
``` bash
sudo apt-get -y install python3-pip
```
  - Install python dependencies
``` bash
cd ml_blink_api/
sudo pip3 install -r requirements.txt
```
  - Create the environmental variables file
```
sudo touch /var/www/ml_blink_api/.env
```
  - Fill the newly created `.env` file assigning the variables declared in `.env.example` their real values
    - The MongoDB URI follows this format: `mongodb://<user>:<pwd>@localhost:27017`

### Restart Apache
  - Restart apache by running the following command:
``` bash
sudo service apache2 restart
```
  - You have successfully deployed a flask application! You should be able to access it at `http://<Floating IP>`

### Debugging
  - If the installation doesn't work, the following commands might be helpful:
    - `tail /var/log/apache2/error.log` will show log errors by the Apache server. If accessing `http://<Floating IP>` returns an error, this command will give you a more detailed description of what happened.
