## Navigate to the `simoc` directory and execute `Steps 1-5 `

## 1. Follow the official guide to set up `docker` software

https://docs.docker.com/install/

## 2. Build a `simoc_server` image

Navigate to the `simoc` directory and run the following command:

```
docker build -t simoc_server_sqlite \
      --build-arg DB_TYPE=sqlite \
      --build-arg APP_PORT=8000 .
```

## 3. Create and deploy a `simoc_server` container in background 

```
docker run -d \
      --name simoc_server_container \
      -v "$(pwd)"/sqlite:/simoc/sqlite \
      -p 8000:8000 \
      simoc_server_sqlite
```

## 4. Init `SQLite` database

```
docker exec -it simoc_server_container python3 create_db.py
```

## 5. Access `SIMOC` application

Navigate to the following URL in your browser to access a SIMOC application - [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 6. Debug deployment

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
docker kill simoc_server_container
docker rm -f simoc_server_container
docker rmi simoc_server_image
```
```
docker build -t simoc_server_sqlite \
      --build-arg DB_TYPE=sqlite \
      --build-arg APP_PORT=8000 .
```
```
docker run -d \
      --name simoc_server_container \
      -v "$(pwd)"/sqlite:/simoc/sqlite \
      -p 8000:8000 \
      simoc_server_sqlite
```

## 8. Reset an `SQLite` database

```
rm sqlite/db.sqlite
docker exec -it simoc_server_container python3 create_db.py
```

