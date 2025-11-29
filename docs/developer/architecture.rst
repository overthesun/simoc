====================
SIMOC's Architecture
====================

The two main components of SIMOC are the **backend** and the **frontend**:

* The **backend** receives the parameters of the simulation, performs all
  the calculations, and returns the result as a list of step data.
* The **frontend** provides a convenient web interface used to visualize
  the results through graphs and tables.

Technically both parts are independent: the backend should be able to work
without the frontend (e.g. from the command line), and the frontend should
be able to work without the backend (e.g. by loading simdata from a file
or by showing live data).  In practice they are mostly used together.

The **backend** is written in Python, whereas the **frontend** is written
in JavaScript.  The source code can be found in two different repositories:

* Backend: https://github.com/overthesun/simoc
* Frontend: https://github.com/overthesun/simoc-web


The Backend Docker Containers
=============================

In order to run locally, the SIMOC backend uses 5 Docker containers
orchestrated using ``docker-compose``:

* ``flask-app``
* ``nginx``
* ``celery-worker``
* ``redis``
* ``simoc-db``

They can be controlled through the ``simoc.py`` script, or directly through
the ``docker`` and ``docker-compose`` commands.

Flask
-----

The ``flask-app`` container runs a Flask application that listens to the
requests and sends back responses to the frontend.  The app is defined in
the ``simoc_server`` directory.

The app also serves the frontend, that is built and included in the
``simoc_server/dist`` directory of the container during deployment.

Nginx
-----

Nginx is the webserver used to forward requests and responses between
the frontend and the backend.

Celery
------

Celery is an asynchronous task queue used to schedule simulation requests
received from the frontend.

Redis
-----

Redis is used to share data between Flask and Celery.

SIMOC DB
--------

This container runs a MySQL instance connected to a Docker volume
that currently only stores the users that created an account through
the SIMOC frontend.


The Frontend Docker Container
=============================

The frontend is build and developed using an additional Docker container,
that can be controlled using the ``simoc-web.py`` script.

This container resides in the frontend repo, and communicates with
the backend containers.

Note that both the frontend container and the build included in the
flask container can be used at the same time, since they use different
``localhost`` ports.
