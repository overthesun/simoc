# Deploy `SIMOC` via `Docker` on `Linux/macOS` (`MySQL` backend)

# 1. Clone `SIMOC` code from `GitHub`
```bash
git clone git@github.com:kstaats/simoc.git
cd simoc/
```

# 2. Configure `Docker` environment

Follow the official guide to set up `Docker` software:
- https://docs.docker.com/install/
- https://docs.docker.com/compose/install/
- https://docs.docker.com/engine/swarm/swarm-tutorial/

Make sure you installed `Docker Engine`, `Docker Compose` and `Swarm` components.

# 3. Configure `SIMOC` deployment

## Set up `Redis` connection details (fill in the `REDIS_PASSWORD` value)
```bash
export REDIS_HOST=redis
export REDIS_PORT=6379
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
```

## Set up `MySQL` configuration (fill in the `DB_PASSWORD` value)
```bash
export DB_TYPE=mysql
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'
```

## Set up `FLASK_SECRET` with any random string value
```bash
export FLASK_SECRET='ENTER_RANDOM_STRING_VALUE'
```

## Set up `HTTP/HTTPS` ports for `SIMOC` application
```bash
export HTTP_PORT=8000
export HTTPS_PORT=8443
```

## Configure `Nginx` proxy service
Open the `nginx/simoc_nginx.conf` file with your favorite text editor and update `listen` and `server_name` parameters in the both `HTTP` and `HTTPS` sections with the corresponding `SIMOC` application ports and domain name:
```
upstream socketio_nodes {
    ip_hash;
    server flask-app:8080;
}

upstream http_nodes {
    server flask-app:8080;
}

# Unencrypted HTTP section
server {
    listen 8000;
    server_name localhost;

    location / {
        include proxy_params;
        proxy_pass http://http_nodes;
    }

    location /socket.io {
        include proxy_params;
        include proxy_ws_params;
        proxy_pass http://socketio_nodes/socket.io;
    }
}

# Secure HTTPS section
server {
    listen 8443 ssl http2;
    server_name localhost;

    ssl_certificate /etc/nginx/certs/cert.pem;
    ssl_certificate_key /etc/nginx/certs/key.pem;

    location / {
        include proxy_params;
        proxy_pass http://http_nodes;
    }

    location /socket.io {
        include proxy_params;
        include proxy_ws_params;
        proxy_pass http://socketio_nodes/socket.io;
    }
}
```

## Generate SSL certificates

Follow your platform-specific instructions to set up either `OpenSSL` or `LibreSSL` on your local machine.

Run the following commands to generate a new `SSL` certificate and provide additional details in
the interactive console menu:
```bash
mkdir certs
openssl req -x509 -newkey rsa:4096 -nodes -out certs/cert.pem -keyout certs/key.pem -days 365
```

Make sure you provide the correct `hostname` value in the `Common Name` section (i.e. `localhost`):
```bash
Generating a 4096 bit RSA private key
...................++
...............++
writing new private key to 'certs/key.pem'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) []:US
State or Province Name (full name) []:Texas
Locality Name (eg, city) []:Austin
Organization Name (eg, company) []:SIMOC
Organizational Unit Name (eg, section) []:
Common Name (eg, fully qualified host name) []:localhost
Email Address []:
```

# 5. Deploy `SIMOC` application

## 5.1. Deploy using `Docker Compose`

### Build `Docker` images
```bash
docker-compose -f docker-compose.mysql.yml build
```

### Set up the number of worker containers to spin up
```bash
export FLASK_WORKERS=2
export CELERY_WORKERS=2
export REDIS_WORKERS=2
```

### Create and start `SIMOC` services
```bash
docker-compose -f docker-compose.mysql.yml up -d \
    --scale celery-worker=${CELERY_WORKERS} \
    --scale flask-app=${FLASK_WORKERS} \
    --scale redis=1 \
    --scale redis-replica=${REDIS_WORKERS}
```

### Debug deployment
Check out [Docker Cheat Sheet](https://github.com/wsargent/docker-cheat-sheet) for more commands.

- Show all running `SIMOC` containers:
```bash
$ docker-compose -f docker-compose.mysql.yml ps

        Name                     Command               State                     Ports
----------------------------------------------------------------------------------------------------
simoc_celery-worker_1   /bin/bash start_worker.sh   Up
simoc_celery-worker_2   /bin/bash start_worker.sh   Up
simoc_flask-app_1       /bin/bash run.sh            Up             0.0.0.0:32836->8000/tcp
simoc_flask-app_2       /bin/bash run.sh            Up             0.0.0.0:32835->8000/tcp
simoc_nginx_1           nginx -g daemon off;        Up             80/tcp, 0.0.0.0:8000->8000/tcp
simoc_redis-replica_1   /entrypoint.sh /run.sh      Up             0.0.0.0:32834->6379/tcp
simoc_redis-replica_2   /entrypoint.sh /run.sh      Up             0.0.0.0:32833->6379/tcp
simoc_redis_1           /entrypoint.sh /run.sh      Up             0.0.0.0:6379->6379/tcp
simoc_simoc-db_1        /entrypoint.sh mysqld       Up (healthy)   0.0.0.0:3306->3306/tcp, 33060/tcp
```
Make sure all services are `Up` and `Healthy`.

- Stream logs from all `SIMOC` services:
```bash
docker-compose -f docker-compose.mysql.yml logs -t -f
```

- Stream logs from the `celery-worker` service:
```bash
docker-compose -f docker-compose.mysql.yml logs -t -f celery-worker
```

- Stream logs from the `flask-app` service:
```bash
docker-compose -f docker-compose.mysql.yml logs -t -f flask-app
```

- Stop all `SIMOC` containers:
```bash
docker-compose -f docker-compose.mysql.yml stop
```

- Start all `SIMOC` containers:
```bash
docker-compose -f docker-compose.mysql.yml start
```

- Stop all `SIMOC` services and remove all containers, images and volumes:
```bash
docker-compose -f docker-compose.mysql.yml down --rmi all --volumes
```

### Scale `SIMOC` components (optional)

Scale the number of `celery-worker` containers to `5`:
```bash
docker-compose -f docker-compose.mysql.yml scale celery-worker=5
```

Scale the number of `flask-app` containers to `5`:
```bash
docker-compose -f docker-compose.mysql.yml scale flask-app=5
```

### Initialize `MySQL` database
Once all `SIMOC` services and containers are up and running, run the following command to create DB schema and populate the agent model:
```bash
$ docker-compose -f docker-compose.mysql.yml exec celery-worker python3 create_db.py

WARNING: Some services (celery-worker, flask-app, nginx, redis, redis-replica, simoc-db) use the 'deploy' key, which will be ignored. Compose does not support 'deploy' configuration - use `docker stack deploy` to deploy to a swarm.
The 'mysql' database at 'mysql+mysqlconnector://root:ENTER_MYSQL_PASSWORD_HERE@simoc-db:3306/simoc' was successfully populated with 'agent_desc.json' config file.
```

If the following error occurs, retry the command in 10-30 seconds:
```
sqlalchemy.exc.OperationalError: (_mysql_exceptions.OperationalError) (2003, "Can't connect to MySQL server on 'simoc-db' (111)")
```

### Re-deploy `SIMOC` on code changes
- Configure environment variables:
```bash
export REDIS_HOST=redis
export REDIS_PORT=6379
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'

export DB_TYPE=mysql
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'

export HTTP_PORT=8000
export HTTPS_PORT=8443
export DOMAIN=localhost
export FLASK_SECRET='ENTER_RANDOM_STRING_VALUE'

export FLASK_WORKERS=2
export CELERY_WORKERS=2
export REDIS_WORKERS=2
```

- Re-build `SIMOC` images:
```bash
docker-compose -f docker-compose.mysql.yml build
```

- Re-deploy `SIMOC` services:
```bash
docker-compose -f docker-compose.mysql.yml up -d \
    --scale celery-worker=${CELERY_WORKERS} \
    --scale flask-app=${FLASK_WORKERS} \
    --scale redis=1 \
    --scale redis-replica=${REDIS_WORKERS}
```

### Reset `MySQL` database
- Stop and remove all `simoc-db` containers and volumes:
```bash
docker-compose -f docker-compose.mysql.yml rm --stop -v simoc-db
docker volume rm simoc_db-data
```

- Re-deploy `simoc-db` service:
```bash
docker-compose -f docker-compose.mysql.yml up -d simoc-db
```

## 5.2. Deploy using `Docker Swarm Mode`

### Set up local `Docker Swarm` cluster

- Initialize a new `Swarm`:
```bash
docker swarm init
```

- Run `docker node ls` command to view information about nodes:
```bash
$ docker node ls

ID                            HOSTNAME            STATUS              AVAILABILITY        MANAGER STATUS      ENGINE VERSION
pbgogvtpuxja0kx2bydzmaplb *   docker-desktop      Ready               Active              Leader              19.03.5
```
Make sure all nodes are `Active` and `Ready`.

### Set up `Docker` image registry
- Deploy up an image registry service to the `Swarm` cluster:
```bash
docker service create --name registry --publish published=5000,target=5000 registry:2
```

- Check its status with `docker service ls`:
```bash
$ docker service ls
ID                  NAME                MODE                REPLICAS            IMAGE               PORTS
qydpdq8dp0rf        registry            replicated          1/1                 registry:2          *:5000->5000/tcp
```

### Set up the number of worker containers to spin up
```bash
export FLASK_WORKERS=2
export CELERY_WORKERS=2
```

### Build `Docker` images
```bash
docker-compose -f docker-compose.swarm.yml build
```

### Push `SIMOC` images to the registry
```bash
docker-compose -f docker-swarm.swarm.yml push
```

### Deploy `SIMOC` application stack to the `Swarm` cluster
```bash
docker stack deploy --compose-file docker-swarm.mysql.yml simoc
```

### Debug deployment

- Show all running `SIMOC` services:
```bash
$ docker stack services simoc
ID                  NAME                  MODE                REPLICAS            IMAGE                                 PORTS
8t179yej5zns        simoc_nginx           replicated          1/1                 nginx:latest                          *:8000->8000/tcp
a30yklx7o3pj        simoc_celery-worker   replicated          2/2                 127.0.0.1:5000/celery-worker:latest
pacm0fjlxpda        simoc_redis           replicated          1/1                 bitnami/redis:latest                  *:6379->6379/tcp
sfkolv7h474i        simoc_simoc-db        replicated          1/1                 mysql/mysql-server:latest             *:3306->3306/tcp
ud5k8fsljb3q        simoc_flask-app       replicated          2/2                 127.0.0.1:5000/flask-app:latest       *:30000->8080/tcp
yc1pzrc78dr9        simoc_redis-replica   replicated          2/2                 bitnami/redis:latest                  *:30001->6379/tcp
```
Make all service `REPLICAS` are fulfilled.

- Show all running `SIMOC` containers:
```bash
$ docker stack ps simoc
ID                  NAME                    IMAGE                                 NODE                DESIRED STATE       CURRENT STATE                ERROR               PORTS
wb6gdlvpqmo3        simoc_celery-worker.1   127.0.0.1:5000/celery-worker:latest   docker-desktop      Running             Running about a minute ago
8440k6as05fb        simoc_redis-replica.1   bitnami/redis:latest                  docker-desktop      Running             Running about a minute ago
vkvv2ll5d4tn        simoc_redis.1           bitnami/redis:latest                  docker-desktop      Running             Running about a minute ago
h6zsc8vijzoz        simoc_simoc-db.1        mysql/mysql-server:latest             docker-desktop      Running             Running 35 seconds ago
miwxlqp1uyu4        simoc_nginx.1           nginx:latest                          docker-desktop      Running             Running about a minute ago
z5a2x73a9lkn        simoc_flask-app.1       127.0.0.1:5000/flask-app:latest       docker-desktop      Running             Running about a minute ago
porrzfopn3dn        simoc_celery-worker.2   127.0.0.1:5000/celery-worker:latest   docker-desktop      Running             Running about a minute ago
ftg4ig70r1gj        simoc_redis-replica.2   bitnami/redis:latest                  docker-desktop      Running             Running about a minute ago
zak52j4q2cfk        simoc_flask-app.2       127.0.0.1:5000/flask-app:latest       docker-desktop      Running             Running about a minute ago
```
Make all containers are `Running` and `ERRORS` logged.

- Fetch logs from `flask-app` service:
```bash
docker service logs -f simoc_flask-app
```

- Fetch logs from `celery-worker` service:
```bash
docker service logs -f simoc_celery-worker
```

### Initialize `MySQL` database
Once all `SIMOC` services and containers are up and running, run the following command to create DB schema and populate the agent model:
```bash
docker exec -ti simoc_celery-worker.1.$(docker service ps -f 'name=simoc_celery-worker.1' simoc_celery-worker -q --no-trunc | head -n1) python3 create_db.py
```

### Scale `SIMOC` components (optional)

Scale the number of `celery-worker` containers to `5`:
```bash
docker service scale simoc_celery-worker=5
```

### Re-deploy `SIMOC` on code changes
```bash
export REDIS_HOST=redis
export REDIS_PORT=6379
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
export DB_TYPE=mysql
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'
export HTTP_PORT=8000
export HTTPS_PORT=8443
export DOMAIN=localhost
export FLASK_SECRET='ENTER_RANDOM_STRING_VALUE'
export FLASK_WORKERS=2
export CELERY_WORKERS=2
docker-compose -f docker-compose.mysql.yml build
docker-compose -f docker-compose.mysql.yml push
docker stack deploy --compose-file docker-compose.mysql.yml simoc
```

### Uninstall instructions

Stop and remove all services and containers:
```bash
docker stack rm simoc
docker service rm registry
```

Turn off `Swarm` mode (local):
```bash
docker swarm leave --force
```

### 6. Access `SIMOC` web application
Navigate to the following `URL` in your browser to access a `SIMOC` application (change `PORT` if needed):
- [http://127.0.0.1:8000](http://127.0.0.1:8000)
- [https://localhost:8443](https://localhost:8443)
