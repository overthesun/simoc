# Deploy `SIMOC` via `Docker` on `Linux/macOS` (`SQLite` backend)

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
```

Set up the number of `Celery Worker` containers to spin up:
```bash
export CELERY_WORKERS=2
```

Set up the number of threads per `Flask Application` container:
```bash
export WSGI_WORKERS=2
```

Set up the listening `HTTP` port for the `Flask Application`:
```bash
export APP_PORT=8000
```

## 4. Build `Docker` images
```bash
docker-compose -f docker-compose.sqlite.yml build
```

## 5. Create and start `SIMOC` service
```bash
docker-compose -f docker-compose.sqlite.yml \
    up -d --scale celery-worker=${CELERY_WORKERS}
```

## 6. Initialize `SQLite` database
```bash
docker-compose -f docker-compose.sqlite.yml \
    exec celery-worker python3 create_db.py
```

## 7. Access `SIMOC` web application
Navigate to the following `URL` in your browser to access a `SIMOC` application (change `PORT` if needed):
- [http://127.0.0.1:8000](http://127.0.0.1:8000)

# Debug Deployment
Check out [Docker Cheat Sheet](https://github.com/wsargent/docker-cheat-sheet) for more commands.

Show all running `Docker Compose` services:

```bash
docker-compose -f docker-compose.sqlite.yml ps
```

The output should look similar to the following which means that all services are up and running:
```bash
        Name                       Command               State           Ports
---------------------------------------------------------------------------------------
simoc_celery-worker_1   /bin/bash start_worker.sh        Up
simoc_celery-worker_2   /bin/bash start_worker.sh        Up
simoc_flask-app_1       /bin/bash run.sh                 Up      0.0.0.0:8000->8000/tcp
simoc_redis_1           docker-entrypoint.sh redis ...   Up      0.0.0.0:6379->6379/tcp
```

Show all containers:
```bash
docker ps -a
```

Fetch logs from all containers:
```bash
docker-compose -f docker-compose.sqlite.yml logs -t -f
```

Fetch logs from a `celery-worker` containers:
```bash
docker-compose -f docker-compose.sqlite.yml \
    logs -t -f celery-worker
```

Fetch logs from a `flask-app` container:
```bash
docker-compose -f docker-compose.sqlite.yml \
    logs -t -f flask-app
```

Stop all `SIMOC` containers:
```bash
docker-compose -f docker-compose.sqlite.yml stop
```

Start all `SIMOC` containers:
```bash
docker-compose -f docker-compose.sqlite.yml start
```

Remove all `SIMOC` containers and images:
```bash
docker-compose -f docker-compose.sqlite.yml down --rmi all
```

# Re-deploy `SIMOC` on file changes

Repeat `Steps 3-5` to re-build and re-deploy the `SIMOC` service.

# Reset `SQLite` database

Remove the `SQLite` database file from the `simoc/sqlite` directory:
```bash
rm sqlite/db.sqlite
```

Re-initialize an `SQLite` database:
```bash
docker-compose -f docker-compose.sqlite.yml \
    exec celery-worker python3 create_db.py
```
