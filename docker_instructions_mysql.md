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

## Set up `HTTP` port for `SIMOC` application
```bash
export APP_PORT=8000
```

## Configure `Nginx` proxy service
Open the `nginx.conf` file with your favorite text editor and update the `listen` parameter with the corresponding `SIMOC` application port:
```
upstream socketio_nodes {
    ip_hash;
    server flask-app:8080;
}

upstream http_nodes {
    server flask-app:8080;
}

server {
    listen 8000;
    server_name _;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://http_nodes;
    }

    location /socket.io {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://socketio_nodes/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

# 4. Build `Docker` images
```bash
docker-compose -f docker-compose.mysql.yml build
```

# 5. Deploy `SIMOC` application

## 5.1. Deploy using `Docker Compose`

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

- Fetch logs from all `SIMOC` services:
```bash
docker-compose -f docker-compose.mysql.yml logs -t -f
```

- Fetch logs from `celery-worker` service:
```bash
docker-compose -f docker-compose.mysql.yml logs -t -f celery-worker
```

- Fetch logs from`flask-app` service:
```bash
docker-compose -f docker-compose.mysql.yml ogs -t -f flask-app
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

export APP_PORT=8000

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

### Push `SIMOC` images to the registry
```bash
docker-compose -f docker-compose.mysql.yml push
```

### Deploy `SIMOC` application stack to the `Swarm` cluster
```bash
docker stack deploy --compose-file docker-compose.mysql.yml simoc
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
