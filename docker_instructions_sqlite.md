## Follow the official guide to set up `docker` software

https://docs.docker.com/install/

## Build a `simoc_server` image

Navigate to the `simoc` directory and run the following command:

```
docker build -t simoc_server_image \
             --build-arg DB_TYPE=sqlite \
             --build-arg PORT=8000 \
             --build-arg WORKERS=5 .
```

## Create and run a `simoc_server` container in background (no logs)

```
docker run --name=simoc_server_container -d --cpus=2 \
           -p 8000:8000 simoc_server_image
```

## Shows running containers

```
docker ps
```

## Continuously fetch the logs from a `simoc_server` container

```
docker logs --follow simoc_server_container
```

## Stop a `simoc_server` container

```
docker stop simoc_server_container
```

## Kill a `simoc_server` container

```
docker kill simoc_server_container
```

## Start a `simoc_server` container

```
docker start simoc_server_container
```

## Stop and start a `simoc_server` container

```
docker restart simoc_server_container
```

## Rebuild and re-run a `simoc_server` container on file changes

```
docker rm -f simoc_server_container
docker rmi simoc_server_image
docker build -t simoc_server_image \
             --build-arg DB_TYPE=sqlite \
             --build-arg PORT=8000 \
             --build-arg WORKERS=5 .
docker run --name=simoc_server_container -d --cpus=2 \
           -p 8000:8000 simoc_server_image
```

Check out [Docker Cheat Sheet](https://github.com/wsargent/docker-cheat-sheet) for more commands.
