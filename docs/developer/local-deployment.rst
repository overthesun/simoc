==========================================
Start ``SIMOC`` locally on ``Linux/macOS``
==========================================

.. warning:: This page describes how to manually install SIMOC locally,
   a process now automated by the ``simoc.py`` script (see :doc:`setup`).
   This page is no longer updated and kept for reference only.


1. Clone ``SIMOC`` code from ``GitHub``
=======================================

::

    git clone git@github.com:kstaats/simoc.git
    cd simoc/


2. Install ``Python 3.6``, ``Redis``, and ``MySQL``
===================================================

Follow the official guides to install ``Python 3.6``, ``Redis``, and ``MySQL``:

* https://www.python.org/downloads/
* https://redis.io/download/
* https://www.mysql.com/downloads/

Start ``Redis`` and ``MySQL`` via ``Docker``.

Instead of manually installing ``Redis`` and ``MySQL`` on a host ``OS``,
follow the instructions below to deploy them as ``Docker`` containers.

Follow the official guide to set up ``Docker`` software:

* https://docs.docker.com/install/

Set up a ``Redis`` connection details (fill in the ``REDIS_PASSWORD`` value)::

    export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'

Start ``Redis`` container::

    docker run -d \
        --name=redis \
        -p 6379:6379 \
        redis redis-server --requirepass $REDIS_PASSWORD


.. _mysql-setup:

Set up the ``MySQL`` configuration (fill in the ``DB_PASSWORD`` value)::

    export DB_PORT=3306
    export DB_NAME=simoc
    export DB_USER=root
    export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'


Start ``MySQL`` container::

    docker run -d \
        --name=simoc-db \
        -p $DB_PORT:$DB_PORT \
        -e MYSQL_USER=$DB_USER \
        -e MYSQL_PASSWORD=$DB_PASSWORD \
        -e MYSQL_DATABASE=$DB_NAME \
        mysql/mysql-server


3. Set up ``Python 3`` virtual environment
==========================================

::

    python3 -m venv simoc-env
    source simoc-env/bin/activate
    python3 -m pip install --upgrade pip setuptools
    python3 -m pip install --upgrade -r requirements.txt


4. Initialize ``MySQL`` database
================================

Set up the ``MySQL`` configuration (fill in the ``DB_PASSWORD`` value)::

    export DB_TYPE=mysql
    export DB_HOST=127.0.0.1
    export DB_PORT=3306
    export DB_NAME=simoc
    export DB_USER=root
    export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'

Run the initialization script::

    python3 create_db.py


5. Start ``Celery Worker`` process
==================================

Set up ``Redis`` connection (fill in the ``REDIS_PASSWORD``)::

    export REDIS_HOST=127.0.0.1
    export REDIS_PORT=6379
    export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'

Start a new ``Celery Worker`` process::

    sh start_worker.sh

Worker logs will start streaming into the ``Terminal`` output.

You can start multiple ``Celery Workers`` to process tasks in parallel.
Make sure you run each worker in a separate ``Terminal`` session and
keep all sessions alive.


6. Start ``Flask Application`` server
=====================================

Open up a new ``Terminal`` session and navigate to the ``simoc`` folder::

    cd /path/to/simoc/folder

Activate ``Python`` virtual environment::

    source simoc-env/bin/activate

Set up a ``Redis`` connection details (fill in the ``REDIS_PASSWORD`` value)::

    export REDIS_HOST=127.0.0.1
    export REDIS_PORT=6379
    export REDIS_PASSWORD='ENTER_REDIS_PASSWORD_HERE'

Set up the ``MySQL`` configuration (fill in the ``DB_PASSWORD`` value)::

    export DB_TYPE=mysql
    export DB_HOST=127.0.0.1
    export DB_PORT=3306
    export DB_NAME=simoc
    export DB_USER=root
    export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'

Start ``SIMOC`` application::

    sh run.sh


7. Access ``SIMOC`` web application
===================================

Navigate to the following ``URL`` in your browser to access a ``SIMOC``
application (change ``PORT`` if needed):

* http://127.0.0.1:8080


Useful commands
===============

Reset ``MySQL`` database (``Docker``)
-------------------------------------

Kill and remove a running ``MySQL-server`` container (if any)::

    docker kill simoc-db
    docker rm -f simoc-db

Repeat the :ref:`MySQL configuration and start the container <mysql-setup>`.

Set up the DB configuration (fill in the ``DB_PASSWORD``)::

    export DB_TYPE=mysql
    export DB_HOST=127.0.0.1
    export DB_PORT=3306
    export DB_NAME=simoc
    export DB_USER=root
    export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'

Re-initialize ``MySQL`` database::

    python3 create_db.py


Run ``SIMOC`` in ``console_mode`` (``JSON`` export)
---------------------------------------------------

Set up the DB configuration (fill in the ``DB_PASSWORD``)::

    export DB_TYPE=mysql
    export DB_HOST=127.0.0.1
    export DB_PORT=3306
    export DB_NAME=simoc
    export DB_USER=root
    export DB_PASSWORD='ENTER_MYSQL_PASSWORD_HERE'

Run a simulation using a sample ``game_config`` file::

    export NO_FLASK=1 && python3 -m simoc_server --console_mode \
        --username test --password test \
        --game_config_path sample_game_config.json \
        --num_steps 100

You should manually interrupt the script when it's finished.

The result data will be stored in ``*_model_records.json`` and
``*_step_records.json`` files.

For custom scenarios, modify the configuration file and set up
the path to the file via ``--game_config_path`` argument.

Kill all running ``Celery Workers``
-----------------------------------

::

    ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9
