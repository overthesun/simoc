# Deploy `SIMOC` via `Docker` on `Linux/macOS` (`MySQL` backend)

# 1. Clone `SIMOC` code from `GitHub`
```bash
git clone git@github.com:kstaats/simoc.git
cd simoc/
```

# 2. Configure `Docker` environment
Follow the official guide to set up `Docker` software:
- https://docs.docker.com/install/
- https://docs.docker.com/compose/install/

Make sure you installed `Docker Engine` and`Docker Compose` components.

# 3. Configure `SIMOC` deployment
## Set up `Redis` connection details (fill in the `REDIS_PASSWORD` value)
```bash
export REDIS_HOST=redis
export REDIS_PORT=6379
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
```

## Set up `MySQL` configuration (fill in the `DB_PASSWORD` value)
```bash
export DB_TYPE=mysql
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'
```

## Set up `FLASK_SECRET` with any random string value
```bash
export FLASK_SECRET='ENTER_RANDOM_STRING_VALUE'
```

## Set up the number of worker containers to spin up
```bash
export FLASK_WORKERS=2
export CELERY_WORKERS=2
```

## Generate dynamic config files (Nginx, Docker)
### Setup environment variables
- `SERVER_NAME` - domain name of the SIMOC host (default: `localhost`)
- `HTTP_PORT` - http port to listen on (default: `8000`)
- `HTTPS_PORT` - https port to listen on (default: `8443`)
- `USE_SSL` - `1` to enable SSL access (default: `0`)
- `USE_CERTBOT` - `1` to use Let's Encrypt certificates (default: `0`)
- `REDIRECT_TO_SSL` - `1` to redirect all HTTP traffic to HTTPS (default: `0`)
- `ADD_BASIC_AUTH` - `1` to enable Basic HTTP authentication (default: `0`)
- `VALID_REFERERS` - domain name of the only referer to allow (default: `''`)
```bash
export SERVER_NAME='localhost'
export HTTP_PORT=8000
export HTTPS_PORT=8443
export USE_SSL=1
export USE_CERTBOT=1
export REDIRECT_TO_SSL=1
export ADD_BASIC_AUTH=1
export VALID_REFERERS='example.com'
```

### Generate configuration files
```bash
python3 generate_configs.py
```
The script will produce `docker-compose.mysql.yml` and `./nginx/simoc_nginx.conf` files.

## Configure additional HTTP authentication (optional)
Make sure you installed a password file creation utility such as `apache2-utils` (Debian, Ubuntu) or `httpd-tools` (RHEL/CentOS/Oracle Linux)

Create a `htpasswd` file and a first user:
```bash
htpasswd -c ./nginx/htpasswd user1
```

Create additional users. Omit the -c flag because the file already exists:
```bash
htpasswd ./nginx/htpasswd user2
```

## Create SSL certificates (optional)
`SIMOC` supports two different SSL configurations:
- Using self-signed SSL certificates that cannot be validated via third-party authority
- Using trusted SSL certificates managed by `Let's Encrypt` (check out the [official website](https://letsencrypt.org/]))

Self-signed certificates are easier to configure which works best for local and testing deployments.
For production deployments we recommend using managed certificates from `Let's Encrypt`.

### Option #1: Use self-signed certificates (`OpenSSL`)
Follow your platform-specific instructions to set up either `OpenSSL` or `LibreSSL` on your local machine.

Run the following commands to generate a new `SSL` certificate and provide additional details in
the interactive console menu:
```bash
mkdir certs
openssl req -x509 -newkey rsa:4096 -nodes -out certs/cert.pem -keyout certs/key.pem -days 365
```

Make sure you provide the correct `hostname` value in the `Common Name` section (i.e. `localhost`):
```bash
Generating a 4096 bit RSA private key
...................++
...............++
writing new private key to 'certs/key.pem'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) []:US
State or Province Name (full name) []:Texas
Locality Name (eg, city) []:Austin
Organization Name (eg, company) []:SIMOC
Organizational Unit Name (eg, section) []:
Common Name (eg, fully qualified host name) []:localhost
Email Address []:
```

### Option #2: Use verified certificates (`Let's Encrypt`)
Create a `Certbot` configuration directory:
```bash
export CERTBOT_PATH="./certbot"
mkdir -p "${CERTBOT_PATH}/conf"
```

Download `Certbot` configuration files:
```bash
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$CERTBOT_PATH/conf/options-ssl-nginx.conf"
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$CERTBOT_PATH/conf/ssl-dhparams.pem"
```

Configure `EMAIL` and `DOMAIN` values for SSL certificates:
```bash
export EMAIL=address@domain.com
export DOMAIN=beta.simoc.space
```

Create domain-specific directories:
```bash
export CERT_PATH="/etc/letsencrypt/live/${DOMAIN}"
mkdir -p "${CERTBOT_PATH}/conf/live/${DOMAIN}"
```

Generate "dummy" certificates:
```bash
docker-compose -f docker-compose.mysql.yml run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:1024 -days 1 \
    -keyout '${CERT_PATH}/privkey.pem' \
    -out '${CERT_PATH}/fullchain.pem' \
    -subj '/CN=localhost'" certbot
```

Start `Nginx` service:
```bash
docker-compose -f docker-compose.mysql.yml up --force-recreate -d nginx
```

Delete "dummy" certificates:
```bash
docker-compose -f docker-compose.mysql.yml run --rm --entrypoint " \
  rm -Rf /etc/letsencrypt/live/${DOMAIN} && \
  rm -Rf /etc/letsencrypt/archive/${DOMAIN} && \
  rm -Rf /etc/letsencrypt/renewal/${DOMAIN}.conf" certbot
```

Request managed certificates from `Let's Encrypt`:
```bash
docker-compose -f docker-compose.mysql.yml run --rm --entrypoint " \
  certbot certonly --webroot -w /var/www/certbot \
    --email ${EMAIL} \
    -d ${DOMAIN} \
    --rsa-key-size 4096 \
    --agree-tos \
    --force-renewal" certbot
```

Reload `Nginx` service:
```bash
docker-compose -f docker-compose.mysql.yml exec nginx nginx -s reload
```


# 5. Deploy `SIMOC` application
## Build `Docker` images
```bash
docker-compose -f docker-compose.mysql.yml build
```

## Start all `SIMOC` services
```bash
docker-compose -f docker-compose.mysql.yml up -d \
    --force-recreate \
    --scale celery-worker=${CELERY_WORKERS} \
    --scale flask-app=${FLASK_WORKERS} \
    --scale redis=1
```

## Debug `SIMOC` deployment
Show all running `SIMOC` containers:
```bash
$ docker-compose -f docker-compose.mysql.yml ps
        Name                      Command                State                 Ports
-----------------------------------------------------------------------------------------------
simoc_celery-worker_1   /bin/bash start_worker.sh     Up (healthy)
simoc_celery-worker_2   /bin/bash start_worker.sh     Up (healthy)
simoc_flask-app_1       /bin/bash run.sh              Up (healthy)   0.0.0.0:32927->8080/tcp
simoc_flask-app_2       /bin/bash run.sh              Up (healthy)   0.0.0.0:32928->8080/tcp
simoc_nginx_1           /bin/sh -c while :; do sle    Up             0.0.0.0:8443->8443/tcp,
                        ...                                          0.0.0.0:8000->8000/tcp
simoc_redis_1           /opt/bitnami/scripts/redis    Up             0.0.0.0:6379->6379/tcp
simoc_simoc-db_1        /entrypoint.sh mysqld         Up (healthy)   0.0.0.0:3306->3306/tcp, 33060/tcp
```
Make sure all services are `Up` and `Healthy`.

Check out [Docker Cheat Sheet](https://github.com/wsargent/docker-cheat-sheet) for more commands.

## Initialize `MySQL` database
Once all `SIMOC` services and containers are up and running, run the following command to create DB schema and populate the agent model:
```bash
docker-compose -f docker-compose.mysql.yml exec celery-worker python3 create_db.py
```

If the following error occurs, retry the command in 10-30 seconds:
```
sqlalchemy.exc.OperationalError: (_mysql_exceptions.OperationalError) (2003, "Can't connect to MySQL server on 'simoc-db' (111)")
```

## Scale `SIMOC` components (optional)
Scale the number of `celery-worker` containers to `5`:
```bash
docker-compose -f docker-compose.mysql.yml scale celery-worker=5
```

Scale the number of `flask-app` containers to `5`:
```bash
docker-compose -f docker-compose.mysql.yml scale flask-app=5
```

## Access `SIMOC` web application
Navigate to the following `URL` in your browser to access a `SIMOC` application (change `PORT` if needed):
- [http://127.0.0.1:8000](http://127.0.0.1:8000)
- [https://localhost:8443](https://localhost:8443)

# 6. Update `SIMOC` application
## Re-deploy `SIMOC` on code changes
- Configure environment variables:
```bash
export REDIS_HOST=redis
export REDIS_PORT=6379
export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'

export DB_TYPE=mysql
export DB_HOST=simoc-db
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'

export HTTP_PORT=8000
export HTTPS_PORT=8443
export FLASK_SECRET='ENTER_RANDOM_STRING_VALUE'

export FLASK_WORKERS=2
export CELERY_WORKERS=2
```

- Re-build `SIMOC` images:
```bash
docker-compose -f docker-compose.mysql.yml build
```

- Re-deploy `SIMOC` services:
```bash
docker-compose -f docker-compose.mysql.yml up -d \
    --force-recreate \
    --scale celery-worker=${CELERY_WORKERS} \
    --scale flask-app=${FLASK_WORKERS} \
    --scale redis=1
```

## Reset `MySQL` database
Stop and remove all `simoc-db` containers and volumes:
```bash
docker-compose -f docker-compose.mysql.yml rm --stop -v simoc-db
docker volume rm simoc_db-data
```

Re-deploy `simoc-db` service:
```bash
docker-compose -f docker-compose.mysql.yml up -d --force-recreate simoc-db
```

# 7. Useful commands
### Stream logs from all `SIMOC` services
```bash
docker-compose -f docker-compose.mysql.yml logs -t -f
```

### Stream logs from the `celery-worker` service
```bash
docker-compose -f docker-compose.mysql.yml logs -t -f celery-worker
```

### Stream logs from the `flask-app` service
```bash
docker-compose -f docker-compose.mysql.yml logs -t -f flask-app
```

### Stop all `SIMOC` containers
```bash
docker-compose -f docker-compose.mysql.yml stop
```

### Start all `SIMOC` containers
```bash
docker-compose -f docker-compose.mysql.yml start
```

### Stop all `SIMOC` services and remove all containers, images and volumes
```bash
docker-compose -f docker-compose.mysql.yml down --rmi all --volumes
```
