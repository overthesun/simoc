# Navigate to the `simoc` directory and execute `Steps 1-6 `

## 1. Follow the official guide to set up `Docker` software

https://docs.docker.com/install/

## 2. Deploy `MySQL` container

Create a `Docker` network service:
```bash
docker network create simoc-net
```

Set up the DB configuration (fill in the password):
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

## 3. Build `SIMOC` image

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

## 4. Create and deploy `SIMOC` container

```bash
docker run -d \
      --name simoc_server_container \
      --net=simoc-net \
      -p $APP_PORT:$APP_PORT \
      simoc_server_mysql
```

## 5. Init `MySQL` database

```bash
docker exec -it simoc_server_container python3 create_db.py
```

## 6. Access `SIMOC` web application
Navigate to the following URL in your browser to access a SIMOC application (change port if needed):<br>
[http://127.0.0.1:8000](http://127.0.0.1:8000)

## 7. Debug deployment
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

## 7. Re-deploy `SIMOC` container on file changes

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

## 8. Reset `MySQL` database

Set up DB configuration (fill in the password):
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

Init `MySQL` database:
```bash
docker exec -it simoc_server_container python3 create_db.py
```

