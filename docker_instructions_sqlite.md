# Setup `SIMOC`on `Linux/macOS`

## 1. Clone `SIMOC` code from `GitHub`
```bash
git clone -b abm_database git@github.com:kstaats/simoc.git
cd simoc/
```

## 2. Follow the official guide to set up `Docker` software

- https://docs.docker.com/install/

## 3. Build `SIMOC` image

Set up `HTTP` port for the `SIMOC` web application:
```bash
export APP_PORT=8000
```

Build a `simoc_server_sqlite` image:
```bash
docker build -t simoc_server_sqlite \
      --build-arg DB_TYPE=sqlite \
      --build-arg APP_PORT=$APP_PORT .
```

## 4. Create and deploy `SIMOC` container

```bash
docker run -d \
      --name simoc_server_container \
      -v "$(pwd)"/sqlite:/simoc/sqlite \
      -p $APP_PORT:$APP_PORT \
      simoc_server_sqlite
```

## 5. Initialize `SQLite` database

```bash
docker exec -it simoc_server_container python3 create_db.py
```

## 6. Access `SIMOC` web application

Navigate to the following `URL` in your browser to access a `SIMOC` application (change `PORT` if needed):
- [http://127.0.0.1:8000](http://127.0.0.1:8000)

# Debug Deployment

Check out [Docker Cheat Sheet](https://github.com/wsargent/docker-cheat-sheet) for more commands.

Show running containers:

```bash
docker ps
```

Show all containers:

```bash
docker ps -a
```

Fetch logs from a `simoc_server_container` container:

```bash
docker logs --follow simoc_server_container
```

Stop a `simoc_server_container` container:

```bash
docker stop simoc_server_container
```

Kill a `simoc_server_container` container:

```bash
docker kill simoc_server_container
```

Start a `simoc_server_container` container:

```bash
docker start simoc_server_container
```

Stop and start a `simoc_server_container` container:

```bash
docker restart simoc_server_container
```

# Re-deploy `SIMOC` on file changes

Set up `HTTP` port for the `SIMOC` web application:
```bash
export APP_PORT=8000
```

Kill and remove a running `simoc_server_container` container (if any):
```bash
docker kill simoc_server_container
docker rm -f simoc_server_container
```

Remove an exiting `simoc_server_sqlite` image (optional):
```bash
docker rmi simoc_server_sqlite
```

Re-build a `simoc_server_sqlite` image:
```bash
docker build -t simoc_server_sqlite \
      --build-arg DB_TYPE=sqlite \
      --build-arg APP_PORT=$APP_PORT .
```

Create and deploy a new `simoc_server_container` container:
```bash
docker run -d \
      --name simoc_server_container \
      -v "$(pwd)"/sqlite:/simoc/sqlite \
      -p $APP_PORT:$APP_PORT \
      simoc_server_sqlite
```

# Reset `SQLite` database

Remove the `SQLite` database file from the `simoc/sqlite` directory:
```bash
rm sqlite/db.sqlite
```

Re-initialize an `SQLite` database:
```bash
docker exec -it simoc_server_container python3 create_db.py
```

