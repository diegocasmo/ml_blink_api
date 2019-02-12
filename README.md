# ML-Blink API

Server API for ML Blink.

*Note: This is still work in progress. More documentation is on its way :).*

### Local Development
  - [Install Docker](https://www.docker.com/products/docker-desktop)
  - Create an `.env` file using `.env.example` as a starting point (i.e., `cp .env.example .env`)
    - Set `ENV=development`
    - There's no need to set the `MONGO_URI` for local development
    - Set `ORIGINS=http://localhost:8080`
  - Run `docker-compose build` to build the Docker services
    - Only run this once or if the Docker container has been updated
  - Run `docker-compose up` to start the Docker container services
  - Run `mongo 127.0.0.1:27017` to start the MongoDB shell
    - This is not required to start the application, but can be useful when you want to manually check the database's collections

### [API Documentation](./ml_blink_api/README.md)
  - Documentation of the endpoints exposed by the ML-Blink API, the methods each of them supports, and the attributes these expect.

### [Server Configuration](./documentation/server-config.md)
  - A guide to configure an Ubuntu 16.04 server to serve the `ml_blink_api` Flask application in the SNIC Cloud.

### [TODO: Deployment](./)
