======================================
Deploy SIMOC via Docker on Linux/macOS
======================================

1. Clone ``SIMOC`` code from ``GitHub``
=======================================

::

    git clone git@github.com:overthesun/simoc.git
    cd simoc/


2. Setup ``Docker`` environment
===============================

Follow the official guide to set up ``Docker`` software:

* https://docs.docker.com/install/
* https://docs.docker.com/compose/install/

Make sure you installed ``Docker Engine`` and``Docker Compose`` components.


3. Configure ``SIMOC`` deployment
=================================

Open ``simoc_docker.env`` file with any text editor, scroll through
the file and update the variable values to configure the deployment::

    vim simoc_docker.env


Update web server configuration:

* ``DOCKER_REPO`` - Docker Hub account name (default: ``''``)
* ``SERVER_NAME`` - domain name of the SIMOC host (default: ``localhost``)
* ``HTTP_PORT`` - http port to listen on (default: ``8000``)
* ``HTTPS_PORT`` - https port to listen on (default: ``8443``)
* ``USE_SSL`` - ``1`` to enable SSL access (default: ``0``)
* ``USE_CERTBOT`` - ``1`` to use Let's Encrypt certificates (default: ``0``)
* ``REDIS_USE_BITNAMI`` = ``1`` use the Bitnami Docker image (default: ``1``)
* ``REDIRECT_TO_SSL`` - ``1`` to redirect all HTTP traffic to HTTPS
  (default: ``0``)
* ``ADD_BASIC_AUTH`` - ``1`` to enable Basic HTTP authentication
  (default: ``0``)
* ``VALID_REFERERS`` - domain name of the only referer to allow
  (default: ``''``)

::

    export DOCKER_REPO='imilov'
    export SERVER_NAME='beta.simoc.space'
    export HTTP_PORT=80
    export HTTPS_PORT=443
    export USE_SSL=1
    export USE_CERTBOT=1
    export REDIRECT_TO_SSL=1
    export ADD_BASIC_AUTH=1
    export VALID_REFERERS='www.example.com'


Setup ``Redis`` and ``MySQL`` root password and a ``Flask`` secret string::

    export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'
    export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'
    export FLASK_SECRET='ENTER_RANDOM_STRING_VALUE'

Update the number of worker containers to spin up (optional)::

    export FLASK_WORKERS=2
    export CELERY_WORKERS=2

Load ``SIMOC`` environment variables::

    source simoc_docker.env

Generate dynamic config files (Nginx, Docker)::

    python3 generate_docker_configs.py

The script will produce ``docker-compose.mysql.yml`` and
``./nginx/simoc_nginx.conf`` files.

Configure Basic HTTP authentication (optional)
----------------------------------------------

Make sure you installed a password file creation utility such as
``apache2-utils`` (Debian, Ubuntu) or ``httpd-tools``
(RHEL/CentOS/Oracle Linux).

Create a ``htpasswd`` file and a first user::

    htpasswd -c ./nginx/htpasswd user1

Create additional users. Omit the -c flag because the file already exists::

    htpasswd ./nginx/htpasswd user2


Create SSL certificates (optional)
----------------------------------

``SIMOC`` supports two different SSL configurations:

* Using self-signed SSL certificates that cannot be validated
  via third-party authority
* Using trusted SSL certificates managed by ``Let's Encrypt``
  (check out the [official website](https://letsencrypt.org/]))

Self-signed certificates are easier to configure which works best
for local and testing deployments.  For production deployments we
recommend using managed certificates from ``Let's Encrypt``.

Option #1: Use self-signed certificates (``OpenSSL``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow your platform-specific instructions to set up either
``OpenSSL`` or ``LibreSSL`` on your local machine.

Run the following commands to generate a new ``SSL`` certificate and
provide additional details in the interactive console menu::

    mkdir certs
    openssl req -x509 -newkey rsa:4096 -nodes -out certs/cert.pem -keyout certs/key.pem -days 365


Make sure you provide the correct ``hostname`` value in the
``Common Name`` section (i.e. ``localhost``)::

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


Option #2: Use verified certificates (``Let's Encrypt``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a ``Certbot`` configuration directory::

    export CERTBOT_PATH="./certbot"
    mkdir -p "${CERTBOT_PATH}/conf"

Download ``Certbot`` configuration files::

    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$CERTBOT_PATH/conf/options-ssl-nginx.conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$CERTBOT_PATH/conf/ssl-dhparams.pem"

Configure ``EMAIL`` for SSL certificates::

    export EMAIL=address@domain.com

Create domain-specific directories::

    export CERT_PATH="/etc/letsencrypt/live/${SERVER_NAME}"
    mkdir -p "${CERTBOT_PATH}/conf/live/${SERVER_NAME}"

Generate "dummy" certificates::

    docker-compose -f ${COMPOSE_FILE} run --rm --entrypoint "\
      openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
        -keyout '${CERT_PATH}/privkey.pem' \
        -out '${CERT_PATH}/fullchain.pem' \
        -subj '/CN=localhost'" certbot

Start ``Nginx`` service::

    docker-compose -f ${COMPOSE_FILE} up --force-recreate -d nginx

Delete "dummy" certificates::

    docker-compose -f ${COMPOSE_FILE} run --rm --entrypoint " \
      rm -Rf /etc/letsencrypt/live/${SERVER_NAME} && \
      rm -Rf /etc/letsencrypt/archive/${SERVER_NAME} && \
      rm -Rf /etc/letsencrypt/renewal/${SERVER_NAME}.conf" certbot

Request managed certificates from ``Let's Encrypt``::

    docker-compose -f ${COMPOSE_FILE} run --rm --entrypoint " \
      certbot certonly --webroot -w /var/www/certbot \
        --email ${EMAIL} \
        -d ${SERVER_NAME} \
        --rsa-key-size 4096 \
        --agree-tos \
        --force-renewal" certbot

Reload ``Nginx`` service::

    docker-compose -f ${COMPOSE_FILE} exec nginx nginx -s reload


4. Deploy ``SIMOC`` application
===============================

Start all ``SIMOC`` components::

    docker-compose -f ${COMPOSE_FILE} up -d \
        --force-recreate \
        --scale celery-worker=${CELERY_WORKERS} \
        --scale flask-app=${FLASK_WORKERS}

Debug ``SIMOC`` deployment by checking all running ``SIMOC`` containers::

    $ docker-compose -f ${COMPOSE_FILE} ps
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

Make sure all services are ``Up`` and ``Healthy``.

Check out `Docker Cheat Sheet <https://github.com/wsargent/docker-cheat-sheet>`_
for more commands.

Initialize ``MySQL`` database
-----------------------------

Once all ``SIMOC`` services and containers are up and running,
run the following command to create DB schema and populate the agent model::

    docker-compose -f ${COMPOSE_FILE} exec celery-worker python3 create_db.py


If the following error occurs, retry the command in 10-30 seconds::

    sqlalchemy.exc.OperationalError: (_mysql_exceptions.OperationalError)
      (2003, "Can't connect to MySQL server on 'simoc-db' (111)")


Scale ``SIMOC`` components (optional)
-------------------------------------
Scale the number of ``celery-worker`` containers to ``5``::

    docker-compose -f ${COMPOSE_FILE} scale celery-worker=5


Scale the number of ``flask-app`` containers to ``5``::

    docker-compose -f ${COMPOSE_FILE} scale flask-app=5


Access ``SIMOC`` web application
--------------------------------

Navigate to the following ``URL`` in your browser to access a ``SIMOC``
application (change ``PORT`` if needed):

* http://127.0.0.1:8000
* https://localhost:8443


5. Update ``SIMOC`` application
===============================

Re-build ``SIMOC`` images
-------------------------

Load ``SIMOC`` environment variables::

    source simoc_docker.env

Login to ``Docker Hub``::

    docker login

Build ``Docker`` images::

    docker build -t simoc_flask .
    docker build -f Dockerfile-celery-worker -t simoc_celery .

Setup version tag for the new images::

    export VERSION=latest

Push new images to ``Docker Hub``::

    docker tag simoc_flask ${DOCKER_REPO}/simoc_flask:${VERSION}
    docker tag simoc_celery ${DOCKER_REPO}/simoc_celery:${VERSION}
    docker push ${DOCKER_REPO}/simoc_flask:${VERSION}
    docker push ${DOCKER_REPO}/simoc_celery:${VERSION}


Re-deploy ``SIMOC`` application
-------------------------------

Load ``SIMOC`` environment variables::

    source simoc_docker.env

Specify the version to deploy::

    export VERSION=latest

Generate ``Docker Compose`` config file::

    python3 generate_docker_configs.py

Pull the latest ``SIMOC`` images::

    docker-compose -f ${COMPOSE_FILE} pull

Re-deploy ``SIMOC`` components::

    docker-compose -f ${COMPOSE_FILE} up -d \
        --force-recreate \
        --scale celery-worker=${CELERY_WORKERS} \
        --scale flask-app=${FLASK_WORKERS}


Reset ``MySQL`` database
------------------------

Stop and remove all ``simoc-db`` containers and volumes::

    docker-compose -f ${COMPOSE_FILE} rm --stop -v simoc-db
    docker volume rm simoc_db-data

Re-deploy ``simoc-db`` service::

    docker-compose -f ${COMPOSE_FILE} up -d --force-recreate simoc-db


6. Useful commands
==================

Stream logs from all ``SIMOC`` services::

    docker-compose -f ${COMPOSE_FILE} logs -t -f

Stream logs from the ``celery-worker`` service::

    docker-compose -f ${COMPOSE_FILE} logs -t -f celery-worker


Stream logs from the ``flask-app`` service::

    docker-compose -f ${COMPOSE_FILE} logs -t -f flask-app

Stop all ``SIMOC`` containers::

    docker-compose -f ${COMPOSE_FILE} stop

Start all ``SIMOC`` containers::

    docker-compose -f ${COMPOSE_FILE} start


Stop all ``SIMOC`` services and remove all containers, images and volumes::

    docker-compose -f ${COMPOSE_FILE} down --rmi all --volumes
