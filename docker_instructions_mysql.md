## Navigate to the `simoc` directory and execute `Steps 1-6 `

## 1. Follow the official guide to set up `docker` software

https://docs.docker.com/install/

## 2. Deploy `MySQL` container

```
docker network create simoc-net
```

```
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD=<ENTER_MYSQL_PASSWORD>
```

```
docker run -d \
      --name=$DB_HOST \
      --net=simoc-net \
      -p $DB_PORT:$DB_PORT \
      -e MYSQL_USER=$DB_USER \
      -e MYSQL_PASSWORD=$DB_PASSWORD \
      -e MYSQL_DATABASE=$DB_NAME \
      mysql/mysql-server
```

## 3. Build a `simoc_server` image

```
export APP_PORT=8000
```
```
docker build -t simoc_server_mysql \
      --build-arg DB_TYPE=mysql \
      --build-arg DB_HOST=$DB_HOST \
      --build-arg DB_PORT=$DB_PORT \
      --build-arg DB_NAME=$DB_NAME \
      --build-arg DB_USER=$DB_USER \
      --build-arg DB_PASSWORD=$DB_PASSWORD \
      --build-arg APP_PORT=$APP_PORT .
```

## 4. Create and deploy a `simoc_server` container in background 

```
docker run -d \
      --name simoc_server_container \
      --net=simoc-net \
      -p $APP_PORT:$APP_PORT \
      simoc_server_mysql
```

## 5. Init an `MySQL` database

```
docker exec -it simoc_server_container python3 create_db.py
```

## 6. Access `SIMOC` application
Navigate to the following URL in your browser to access a SIMOC application - [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 7. Debug deployment
Check out [Docker Cheat Sheet](https://github.com/wsargent/docker-cheat-sheet) for more commands.

### Show running containers

```
docker ps
```

### Show all containers

```
docker ps -a
```

### Fetch logs from a `simoc_server` container

```
docker logs --follow simoc_server_container
```

### Stop a `simoc_server` container

```
docker stop simoc_server_container
```

### Kill a `simoc_server` container

```
docker kill simoc_server_container
```

### Start a `simoc_server` container

```
docker start simoc_server_container
```

### Stop and start a `simoc_server` container

```
docker restart simoc_server_container
```

## 7. Rebuild and re-deploy a `simoc_server` container on file changes

```
export APP_PORT=8000
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD=<ENTER_MYSQL_PASSWORD>
```
```
docker kill simoc_server_container
docker rm -f simoc_server_container
docker rmi simoc_server_image
```
```
docker build -t simoc_server_mysql \
      --build-arg DB_TYPE=mysql \
      --build-arg DB_HOST=$DB_HOST \
      --build-arg DB_PORT=$DB_PORT \
      --build-arg DB_NAME=$DB_NAME \
      --build-arg DB_USER=$DB_USER \
      --build-arg DB_PASSWORD=$DB_PASSWORD \
      --build-arg APP_PORT=$APP_PORT .
```
```
docker run -d \
      --name simoc_server_container \
      --net=simoc-net \
      -p $APP_PORT:$APP_PORT \
      simoc_server_mysql
```

## 8. Reset `MySQL` database
```
export APP_PORT=8000
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD=<ENTER_MYSQL_PASSWORD>
```
```
docker kill $DB_HOST
docker rm -f $DB_HOST
```
```
docker run -d \
      --name=$DB_HOST \
      --net=simoc-net \
      -p $DB_PORT:$DB_PORT \
      -e MYSQL_USER=$DB_USER \
      -e MYSQL_PASSWORD=$DB_PASSWORD \
      -e MYSQL_DATABASE=$DB_NAME \
      mysql/mysql-server
```
```
docker kill simoc_server_container
docker rm -f simoc_server_container
```
```
docker run -d \
      --name simoc_server_container \
      --net=simoc-net \
      -p $APP_PORT:$APP_PORT \
      simoc_server_mysql
```
```
docker exec -it simoc_server_container python3 create_db.py
```

