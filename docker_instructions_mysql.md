# Deploy `SIMOC` via `Docker` on `Linux/macOS` (`MySQL` backend)

## 1. Clone `SIMOC` code from `GitHub`
```bash
git clone git@github.com:kstaats/simoc.git
cd simoc/
```

## 2. Follow the official guide to set up `Docker` software

Make sure you installed both `Docker Engine` and `Docker Compose` components:
- https://docs.docker.com/install/
- https://docs.docker.com/compose/install/

## 3. Set up the configuration

Set up a `Redis` connection details (fill in the `REDIS_PASSWORD` value):
```bash
export REDIS_HOST=redis
export REDIS_PORT=6379
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
export REDIS_WORKERS=2
```

Set up the `MySQL` configuration (fill in the `DB_PASSWORD` value):
```bash
export DB_TYPE=mysql
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'
```

Set up the number of `Celery Worker` containers to spin up:
```bash
export CELERY_WORKERS=2
```

Set up the number of `Flask Backend` containers:
```bash
export FLASK_WORKERS=2
```

Set up the listening `HTTP` port for the `Flask Backend`:
```bash
export APP_PORT=8000
```

Update `nginx.conf` file with the corresponding `Flask Backend` port:
```
upstream socketio_nodes {
    ip_hash;
    server flask-app:8000;
}

upstream http_nodes {
    server flask-app:8000;
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

## 4. Build `Docker` images
```bash
docker-compose -f docker-compose.mysql.yml build
```

## 5. Create and start `SIMOC` service
```bash
docker-compose -f docker-compose.mysql.yml up -d \
    --scale celery-worker=${CELERY_WORKERS} \
    --scale flask-app=${FLASK_WORKERS} \
    --scale redis=1 \
    --scale redis-replica=${REDIS_WORKERS}
```

## 6. Initialize `MySQL` database
```bash
docker-compose -f docker-compose.mysql.yml \
    exec celery-worker python3 create_db.py
```

If the following error occurs, wait for 10-30 seconds and retry again:
```
sqlalchemy.exc.OperationalError: (_mysql_exceptions.OperationalError) (2003, "Can't connect to MySQL server on 'simoc-db' (111)")
```

## 7. Access `SIMOC` web application
Navigate to the following `URL` in your browser to access a `SIMOC` application (change `PORT` if needed):
- [http://127.0.0.1:8000](http://127.0.0.1:8000)

# Debug Deployment
Check out [Docker Cheat Sheet](https://github.com/wsargent/docker-cheat-sheet) for more commands.

Show all running `Docker Compose` services:

```bash
docker-compose -f docker-compose.mysql.yml ps
```

The output should look similar to the following which means that all services are up and running:
```bash
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

Show all containers:
```bash
docker ps -a
```

Fetch logs from all containers:
```bash
docker-compose -f docker-compose.mysql.yml logs -t -f
```

Fetch logs from a `celery-worker` containers:
```bash
docker-compose -f docker-compose.mysql.yml \
    logs -t -f celery-worker
```

Fetch logs from a `flask-app` containers:
```bash
docker-compose -f docker-compose.mysql.yml \
    logs -t -f flask-app
```

Stop all `SIMOC` containers:
```bash
docker-compose -f docker-compose.mysql.yml stop
```

Start all `SIMOC` containers:
```bash
docker-compose -f docker-compose.mysql.yml start
```

Remove all `SIMOC` containers and images:
```bash
docker-compose -f docker-compose.mysql.yml down --rmi all
```

# Re-deploy `SIMOC` on file changes

Repeat `Steps 3-5` to re-build and re-deploy the `SIMOC` service.

# Reset `MySQL` database

Kill and remove a running `MySQL` container (if any):
```bash
docker-compose -f docker-compose.mysql.yml stop simoc-db
docker-compose -f docker-compose.mysql.yml rm simoc-db
```

Repeat `Steps 5-6` to re-build and re-deploy the `SIMOC` service.

