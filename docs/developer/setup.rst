================
Setting up SIMOC
================

Regular users can access SIMOC at https://ngs.simoc.space.

If you want to run SIMOC on your machine or if you are
a SIMOC developer, you can follow the instructions below
to install SIMOC on your local machine.

.. note::

   SIMOC is mainly developed on Linux and the setup process is
   optimized for Debian/Ubuntu. It is possible to run it on
   MacOS and Windows (using WSL), but some dependencies must be
   installed manually.


Initial Setup
=============

These instructions explain how to set up SIMOC locally.
You will need to install the SIMOC backend (``simoc``) and
optionally the web frontend (``simoc-web``).

1. (Optional) If you are using a system other than Debian/Ubuntu,
   :ref:`install the dependencies <deps>` manually first.

2. Clone the SIMOC repositories using the following commands::

      git clone https://github.com/overthesun/simoc.git
      git clone https://github.com/overthesun/simoc-web.git  # optional

   If you are a SIMOC developer with write access, you can use these
   commands instead::

      git clone git@github.com:overthesun/simoc.git
      git clone git@github.com:overthesun/simoc-web.git  # optional

   The ``simoc-web`` repository is only needed for the web frontend.

3. (Optional) To set up the web frontend run::

      cd simoc-web
      python3 simoc-web.py setup

   At the end of the setup it will ask you about copying the ``dist``
   directory that contains the built frontend --- answer ``Y``.

4. To set up the backend run::

      # cd ..  # return to parent dir if you are in simoc-web/
      cd simoc
      python3 simoc.py setup

.. note::

   During the setup of either the frontend or backend (steps 3/4),
   you might be asked to log out and log in again (or restart your machine)
   to complete the installation of Docker.
   After logging back in, you can resume the installation
   by running the same command again.


If you are a developer and want to contribute to the project,
you will find useful information in the :ref:`repo-setup` section.


.. _deps:

Installing Dependencies
=======================

SIMOC requires three dependencies:

* docker_
* docker-compose_
* Jinja2_

On Debian/Ubuntu, the ``simoc.py`` script will check if any of these
dependencies are missing, and install them automatically using ``apt``.

On other systems you will have to install them manually.

.. _docker: https://docs.docker.com/engine/install/
.. _docker-compose: https://docs.docker.com/compose/install/
.. _Jinja2: https://pypi.org/project/Jinja2/


Using ``simoc.py``
==================

You can run ``python3 simoc.py <command>`` to control SIMOC:

* Initial setup: ``simoc.py setup``
* Remove SIMOC: ``simoc.py teardown``
* Reinstall: ``simoc.py reset``
* Start/update the containers: ``simoc.py up``
* Stop/remove the containers: ``simoc.py down``
* Show the help: ``simoc.py --help``

Run ``python3 simoc.py --help`` for the full list of commands.


Running the dev backend
-----------------------

If you are editing the backend code and want your changes
to be reflected in the Docker containers, you can mount
the local directory in the container using::

   python3 simoc.py --with-dev-backend

Since the directory is shared, you can keep making changes and
they will automatically be visible within the container,
but you might need to restart the containers using ``simoc.py restart``.


Using a custom ``agent_desc.json``
----------------------------------

.. note::  Due to recent changes and improvements to the ways
   agents are handled, this command doesn't currently work.
   We are working on restoring this functionality.

It is also possible to specify a custom ``agent_desc.json`` file::

   python3 simoc.py --agent-desc agent_desc.json reset-db

This will override the ``agent_desc.json`` file in the container
with the file specified after the ``--agent-desc`` option.  Since
the file must be loaded in the DB, the ``reset-db`` command is used
to reinitialize the DB.

If you want to return to the original version of the file, simply run::

   python3 simoc.py reset-db
