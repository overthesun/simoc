# Setup `SIMOC`on `Linux/macOS`

## 1. Clone `SIMOC` code from `GitHub`
```bash
git clone -b abm_database git@github.com:kstaats/simoc.git
cd simoc/
```

## 2. Follow the official guide to set up `Docker` software

- https://docs.docker.com/install/

## 3. Deploy `MySQL` container

Create a `Docker` network service:
```bash
docker network create simoc-net
```

Set up the DB configuration (fill in the `DB_PASSWORD`):
```bash
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD=<ENTER_MYSQL_PASSWORD>
```

Create and deploy a `MySQL-server` container:
```bash
docker run -d \
      --name=$DB_HOST \
      --net=simoc-net \
      -p $DB_PORT:$DB_PORT \
      -e MYSQL_USER=$DB_USER \
      -e MYSQL_PASSWORD=$DB_PASSWORD \
      -e MYSQL_DATABASE=$DB_NAME \
      mysql/mysql-server
```

## 4. Build `SIMOC` image

Set up `HTTP` port for the `SIMOC` web application:
```bash
export APP_PORT=8000
```
Build a `simoc_server_mysql` image:
```bash
docker build -t simoc_server_mysql \
      --build-arg DB_TYPE=mysql \
      --build-arg DB_HOST=$DB_HOST \
      --build-arg DB_PORT=$DB_PORT \
      --build-arg DB_NAME=$DB_NAME \
      --build-arg DB_USER=$DB_USER \
      --build-arg DB_PASSWORD=$DB_PASSWORD \
      --build-arg APP_PORT=$APP_PORT .
```

## 5. Create and deploy `SIMOC` container

```bash
docker run -d \
      --name simoc_server_container \
      --net=simoc-net \
      -p $APP_PORT:$APP_PORT \
      simoc_server_mysql
```

## 6. Initialize `MySQL` database

```bash
docker exec -it simoc_server_container python3 create_db.py
```

## 7. Access `SIMOC` web application
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

Set up the DB configuration (fill in the password):
```bash
export APP_PORT=8000
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD=<ENTER_MYSQL_PASSWORD>
```

Kill and remove a running `simoc_server_container` container (if any):
```bash
docker kill simoc_server_container
docker rm -f simoc_server_container
```

Remove an exiting `simoc_server_mysql` image (optional):
```bash
docker rmi simoc_server_mysql
```

Re-build a `simoc_server_mysql` image:
```bash
docker build -t simoc_server_mysql \
      --build-arg DB_TYPE=mysql \
      --build-arg DB_HOST=$DB_HOST \
      --build-arg DB_PORT=$DB_PORT \
      --build-arg DB_NAME=$DB_NAME \
      --build-arg DB_USER=$DB_USER \
      --build-arg DB_PASSWORD=$DB_PASSWORD \
      --build-arg APP_PORT=$APP_PORT .
```

Create and deploy a new `simoc_server_container` container:
```bash
docker run -d \
      --name simoc_server_container \
      --net=simoc-net \
      -p $APP_PORT:$APP_PORT \
      simoc_server_mysql
```

# Reset `MySQL` database

Set up DB configuration (fill in the `DB_PASSWORD`):
```bash
export APP_PORT=8000
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD=<ENTER_MYSQL_PASSWORD>
```

Kill and remove a running `MySQL` docker container (if any):
```bash
docker kill $DB_HOST
docker rm -f $DB_HOST
```

Create and deploy a new `MySQL-server` container:
```bash
docker run -d \
      --name=$DB_HOST \
      --net=simoc-net \
      -p $DB_PORT:$DB_PORT \
      -e MYSQL_USER=$DB_USER \
      -e MYSQL_PASSWORD=$DB_PASSWORD \
      -e MYSQL_DATABASE=$DB_NAME \
      mysql/mysql-server
```

Kill and remove a running `simoc_server_container` container (if any):
```bash
docker kill simoc_server_container
docker rm -f simoc_server_container
```

Create and deploy a new `simoc_server_container` container:
```bash
docker run -d \
      --name simoc_server_container \
      --net=simoc-net \
      -p $APP_PORT:$APP_PORT \
      simoc_server_mysql
```

Re-initialize `MySQL` database:
```bash
docker exec -it simoc_server_container python3 create_db.py
```

