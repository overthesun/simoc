# Setup `SIMOC`on `Linux/macOS`

## 1. Clone `SIMOC` code from `GitHub`
```bash
git clone -b abm_database git@github.com:kstaats/simoc.git
cd simoc/
```

## 2. Follow the official guide to install `Docker`

- https://docs.docker.com/install/

## 3. Create `Docker` network service
```bash
docker network create simoc-net
```

## 4. Deploy `Redis` container 

Set up `Redis` connection: (fill in the `DB_PASSWORD`):
```bash
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
```

Start a `Redis` container
```bash
docker run -d \
    --name=redis \
    --net=simoc-net \
    -p 6379:6379 \
    redis redis-server --requirepass $REDIS_PASSWORD
```

## 5. Build `Celery Worker` image

Set up `Redis` connection: (fill in the `DB_PASSWORD`):
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
    --build-arg REDIS_HOST=$REDIS_HOST \
    --build-arg REDIS_PORT=$REDIS_PORT \
    --build-arg CELERY_THREADS=$CELERY_THREADS .
```

## 6. Deploy `Celery Worker` container
```bash
docker run -d \
      --name simoc_celery_worker_container \
      --net=simoc-net \
      -v "$(pwd)"/sqlite:/simoc/sqlite \
      simoc_celery_worker
```

## 7. Build `Flask Application` image

Set up `HTTP` port for the `SIMOC` web application:
```bash
export APP_PORT=8000
```

Build a `simoc_flask_sqlite` image:
```bash
docker build -t simoc_flask_sqlite \
      --build-arg DB_TYPE=sqlite \
      --build-arg REDIS_HOST=$REDIS_HOST \
      --build-arg REDIS_PORT=$REDIS_PORT \
      --build-arg APP_PORT=$APP_PORT .
```

## 8. Deploy `Flask Application` container

```bash
docker run -d \
      --name simoc_flask_container \
       --net=simoc-net \
      -v "$(pwd)"/sqlite:/simoc/sqlite \
      -p $APP_PORT:$APP_PORT \
      simoc_flask_sqlite
```

## 9. Initialize `SQLite` database

```bash
docker exec -it simoc_flask_container python3 create_db.py
```


## 10. Access `SIMOC` web application

Navigate to the following `URL` in your browser to access a `SIMOC` application (change `PORT` if needed):
- [http://127.0.0.1:8000](http://127.0.0.1:8000)

# Debug Deployment

Check out [Docker Cheat Sheet](https://github.com/wsargent/docker-cheat-sheet) for more commands.

Show running containers:

```bash
docker ps
```

The output should look similar to the following which means that `SIMOC` is up and running:
```bash
CONTAINER ID        IMAGE                 COMMAND                  CREATED              STATUS              PORTS                    NAMES
92dbce0e5548        simoc_flask_sqlite    "/bin/bash run.sh"       About a minute ago   Up About a minute   0.0.0.0:8000->8000/tcp   simoc_flask_container
91c0923f93f6        simoc_celery_worker   "/bin/bash start_wor…"   2 minutes ago        Up 2 minutes                                 simoc_celery_worker_container
7d92d28881bd        redis                 "docker-entrypoint.s…"   About an hour ago    Up About an hour    0.0.0.0:6379->6379/tcp   redis
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

Remove existing `simoc_flask_sqlite` and `simoc_celery_worker` images (optional):
```bash
docker rmi simoc_flask_sqlite simoc_celery_worker
```

Repeat `Steps 5-8` to re-build and re-deploy the `SIMOC` application.

# Reset `SQLite` database

Remove the `SQLite` database file from the `simoc/sqlite` directory:
```bash
rm sqlite/db.sqlite
```

Re-initialize an `SQLite` database:
```bash
docker exec -it simoc_flask_container python3 create_db.py
```

