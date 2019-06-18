# Setup `SIMOC`on `Linux/macOS`

## 1. Clone `SIMOC` code from `GitHub`
```bash
git clone -b celery_integration git@github.com:kstaats/simoc.git
cd simoc/
```

## 2. Follow the official guide to set up `Docker` software

- https://docs.docker.com/install/

## 3. Create `Docker` network service
```bash
docker network create simoc-net
```

## 4. Deploy `MySQL` container

Set up the DB configuration (fill in the `DB_PASSWORD`):
```bash
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'
```

Create and deploy a `MySQL-server` container:
```bash
docker run -d \
      --name=simoc-db \
      --net=simoc-net \
      -p $DB_PORT:$DB_PORT \
      -e MYSQL_USER=$DB_USER \
      -e MYSQL_PASSWORD=$DB_PASSWORD \
      -e MYSQL_DATABASE=$DB_NAME \
      mysql/mysql-server
```

## 5. Deploy `Redis` container 

Set up `Redis` password (fill in the `REDIS_PASSWORD`):
```bash
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
```

Start a `Redis` container:
```bash
docker run -d \
    --name=redis \
    --net=simoc-net \
    -p 6379:6379 \
    redis redis-server --requirepass $REDIS_PASSWORD
```

## 6. Build `Celery Worker` image

Set up `Redis` connection:
```bash
export REDIS_HOST=redis
export REDIS_PORT=6379
```

Set up number of threads per `Celery` worker:
```bash
export CELERY_THREADS=2
```

Build a `simoc_celery_worker` image:
```bash
docker build -f celery_worker/Dockerfile \
    -t simoc_celery_worker \
    --build-arg DB_TYPE=mysql \
    --build-arg REDIS_HOST=$REDIS_HOST \
    --build-arg REDIS_PORT=$REDIS_PORT \
    --build-arg REDIS_PASSWORD=$REDIS_PASSWORD \
    --build-arg DB_HOST=$DB_HOST \
    --build-arg DB_PORT=$DB_PORT \
    --build-arg DB_NAME=$DB_NAME \
    --build-arg DB_USER=$DB_USER \
    --build-arg DB_PASSWORD=$DB_PASSWORD \
    --build-arg CELERY_THREADS=$CELERY_THREADS .
```

## 7. Deploy `Celery Worker` container
```bash
docker run -d \
      --name simoc_celery_worker_container \
      --net=simoc-net \
      simoc_celery_worker
```

## 8. Build `Flask Application` image

Set up `HTTP` port for the `SIMOC` web application:
```bash
export APP_PORT=8000
```


Build a `simoc_flask_mysql` image:
```bash
docker build -t simoc_flask_mysql \
      --build-arg DB_TYPE=mysql \
      --build-arg REDIS_HOST=$REDIS_HOST \
      --build-arg REDIS_PORT=$REDIS_PORT \
      --build-arg REDIS_PASSWORD=$REDIS_PASSWORD \
      --build-arg DB_HOST=$DB_HOST \
      --build-arg DB_PORT=$DB_PORT \
      --build-arg DB_NAME=$DB_NAME \
      --build-arg DB_USER=$DB_USER \
      --build-arg DB_PASSWORD=$DB_PASSWORD \
      --build-arg APP_PORT=$APP_PORT .
```

## 9. Deploy `Flask Application` container

```bash
docker run -d \
      --name simoc_flask_container \
      --net=simoc-net \
      -p $APP_PORT:$APP_PORT \
      simoc_flask_mysql
```

## 10. Initialize `MySQL` database

```bash
docker exec -it simoc_flask_container python3 create_db.py
```

## 11. Access `SIMOC` web application
Navigate to the following `URL` in your browser to access a `SIMOC` application (change `PORT` if needed):
- [http://127.0.0.1:8000](http://127.0.0.1:8000)

# Debug Deployment
Check out [Docker Cheat Sheet](https://github.com/wsargent/docker-cheat-sheet) for more commands.

Show running containers:

```bash
docker ps
```

The output should look similar to the following which means that both `MySQL-server` and `SIMOC` are up and running:
```bash
CONTAINER ID        IMAGE                 COMMAND                  CREATED              STATUS                   PORTS                               NAMES
bfa5a2bb60c5        simoc_flask_mysql     "/bin/bash run.sh"       About a minute ago   Up About a minute        0.0.0.0:8000->8000/tcp              simoc_flask_container
0e43221e6688        simoc_celery_worker   "/bin/bash start_wor…"   3 minutes ago        Up 3 minutes                                                 simoc_celery_worker_container
7671bd696d55        redis                 "docker-entrypoint.s…"   6 minutes ago        Up 6 minutes             0.0.0.0:6379->6379/tcp              redis
57a3c4de603d        mysql/mysql-server    "/entrypoint.sh mysq…"   7 minutes ago        Up 7 minutes (healthy)   0.0.0.0:3306->3306/tcp, 33060/tcp   simoc-db
```

Show all containers:

```bash
docker ps -a
```

Fetch logs from a `simoc_flask_container` container:

```bash
docker logs --follow simoc_flask_container
```

Fetch logs from a `simoc_celery_worker_container` container:

```bash
docker logs --follow simoc_celery_worker_container
```

# Re-deploy `SIMOC` on file changes

Kill running `simoc_flask_container` and `simoc_celery_worker_container` containers (if any):
```bash
docker kill simoc_flask_container simoc_celery_worker_container
```

Remove existing `simoc_flask_container` and `simoc_celery_worker_container` containers:
```bash
docker rm -f simoc_flask_container simoc_celery_worker_container
```

Remove existing `simoc_flask_mysql` and `simoc_celery_worker` images (optional):
```bash
docker rmi simoc_flask_mysql simoc_celery_worker
```

Repeat `Steps 6-9` to re-build and re-deploy the `SIMOC` application.

# Reset `MySQL` database

Kill and remove a running `MySQL-server` container (if any):
```bash
docker kill simoc-db
docker rm -f simoc-db
```

Kill running `simoc_flask_container` and `simoc_celery_worker_container` containers (if any):
```bash
docker kill simoc_flask_container simoc_celery_worker_container
```

Remove existing `simoc_flask_container` and `simoc_celery_worker_container` containers:
```bash
docker rm -f simoc_flask_container simoc_celery_worker_container
```

Repeat `Steps 4, 7, 9 and 10` to re-deploy the `MySQL-server` and `SIMOC` containers.


