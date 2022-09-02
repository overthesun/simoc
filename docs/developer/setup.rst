================
Setting up SIMOC
================

Initial Setup
=============

For SIMOC users
---------------
These instructions explain how to set up SIMOC locally on a Linux machine.
You will need to install the SIMOC backend (``simoc``) and
optionally to web frontend (``simoc-web``).


1. Create a GitHub account, request access to the repos, and
   then `generate a personal access token <pat_>`_.
2. Clone the SIMOC repositories using the following commands
   (enter your GitHub username and personal access token when asked)::

      git clone https://github.com/overthesun/simoc.git
      git clone https://github.com/overthesun/simoc-web.git  # optional

   The ``simoc-web`` repository is only needed for the web frontend.
3. (Optional) To set up the web frontend run::

      cd simoc-web
      python3 simoc-web.py setup

4. To set up the backend run::

      # if you just set up the frontend in simoc-web/ run this first
      # cd ..
      cd simoc
      python3 simoc.py setup

5. Access SIMOC at http://localhost:8000/.

.. note::

   During the setup of either the frontend or backend (steps 3/4),
   you might be asked to log out and log in again (or restart your machine).
   After logging back in, you can resume the installation
   by running the same command again.


For SIMOC developers
--------------------

1. `Generate and upload an SSH key <ssh-key_>`_.
2. Clone the SIMOC repositories::

      git clone git@github.com:overthesun/simoc.git
      git clone git@github.com:overthesun/simoc-web.git  # optional
      git clone git@github.com:overthesun/simoc-sam.git  # optional

3. Follow steps 3-5 from the section above.

For more information see also :ref:`repo-setup`.

.. _pat: https://github.com/settings/tokens/new?description=SIMOC%20token&scopes=repo
.. _ssh-key: https://github.com/settings/keys


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
