================
Setting up SIMOC
================

Initial Setup
=============

In order to set up SIMOC on your local Linux/MacOS machine,
you need to follow the following steps:

1. Clone the SIMOC repository:
   ``git clone https://github.com/overthesun/simoc.git``
2. Install ``docker`` and ``docker-compose``:
   ``apt install docker docker-compose``
3. Run ``python3 simoc.py setup``
4. Access SIMOC at http://127.0.0.1:8000/

For more information see also :ref:`repo-setup`.


Using ``simoc.py``
==================

You can use the ``simoc.py`` script to control SIMOC:

* Initial setup: ``simoc.py setup``
* Remove SIMOC: ``simoc.py teardown``
* Reinstall: ``simoc.py reset``
* Start/update the containers: ``simoc.py up``
* Stop/remove the containers: ``simoc.py down``
* Show the help: ``simoc.py --help``

Please refer to the ``--help`` for the full list of commands.


Running the dev backend
-----------------------

When you start SIMOC, it will use the code included in the containers
retrieved from Docker Hub.  If you want to run the clone from your local
repository, you can use::

   python3 simoc.py --with-dev-backend

This will mount the local directory in the container, so that every
change you did to the source will be applied.  Since the directory is
shared, you can keep making changes and they will automatically be
reflected within the container, but you might need to restart the
containers using ``simoc.py restart``.


Using a custom ``agent_desc.json``
----------------------------------

It is also possible to specify a custom ``agent_desc.json`` file::

   python3 simoc.py --agent-desc agent_desc.json reset-db

This will override the ``agent_desc.json`` file in the container
with the file specified after the ``--agent-desc`` option.  Since
the file must be loaded in the DB, the ``reset-db`` command is used
to reinitialize the DB.

If you want to return to the original version of the file, simply run::

   python3 simoc.py reset-db
