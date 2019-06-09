## Follow the official guide to set up `docker` software

https://docs.docker.com/install/

## Build a `simoc_server` image

Navigate to the `simoc` directory and run the following command:

```
docker build -t simoc_server .
```

## Create and run a `simoc_server` container in background (no logs)

```
docker run --name=simoc_server -d -p 8000:8000 simoc_server
```

## Shows running containers

```
docker ps
```

## Continuously fetch the logs from a `simoc_server` container

```
docker logs --follow simoc_server
```

## Stop a `simoc_server` container

```
docker stop simoc_server
```

## Kill a `simoc_server` container

```
docker kill simoc_server
```

## Start a `simoc_server` container

```
docker start simoc_server
```

## Stop and start a `simoc_server` container

```
docker restart simoc_server
```

## Rebuild and re-run a `simoc_server` container on file changes

```
docker build -t simoc_server .
docker rm -f simoc_server
docker run --name=simoc_server -d -p 8000:8000 simoc_server
```

Check out [Docker Cheat Sheet](https://github.com/wsargent/docker-cheat-sheet) for more commands.
