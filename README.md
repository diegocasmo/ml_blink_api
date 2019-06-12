# ML-Blink API

Server API for ML Blink.

### Local Development
  - [Install Docker](https://www.docker.com/products/docker-desktop)
  - Create an `.env` file using `.env.example` as a starting point (i.e., `cp .env.example .env`)
    - Set `FLASK_ENV=development`
    - There's no need to set the `MONGO_URI` for local development
    - Set `ORIGINS=http://localhost:8080`
  - Unzip the beta-pack dataset images (`PanSTARRS_ltd` and `USNO1001`) in `/ml_blink_api/static/beta_images` in their corresponding directories
  - Run `docker-compose build` to build the Docker services
    - Only run this once or if the Dockerfile has been updated
  - Start: `docker-compose up`
  - Stop : `docker-compose down`
  - Run `mongo 127.0.0.1:27017` to start the MongoDB shell
    - This is not required to start the application, but can be useful when you want to manually check the database's collections
  - Rebuild the application (changes to the `requirements.txt` or Docker configuration file require a rebuild):
``` bash
docker-compose up --build
```

### [API Documentation](./ml_blink_api/README.md)
  - Documentation of the endpoints exposed by the ML-Blink API, the methods each of them supports, and the attributes these expect.

### [Server Configuration](./documentation/server-config.md)
  - A guide to configure an Ubuntu 16.04 server to serve the `ml_blink_api` Flask application in the SNIC Cloud.

### Deployment
  - This is a very rudimentary deployment script. It assumes the server is setup as explained in the [server configuration guide](./documentation/server-config.md).
  - SSH in the server by running `ssh -i <file_name>.pem ubuntu@<FLOATING_IP_ADDRESS>` and run:
``` bash
sudo systemctl stop celeryd
sudo service apache2 stop
cd /var/www/ml_blink_api
sudo git pull
sudo pip3 install -r requirements.txt
sudo service apache2 restart
sudo systemctl restart celeryd
```
