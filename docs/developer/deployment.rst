==================
SIMOC's Deployment
==================

SIMOC is currently available in two different locations: *beta* and *NGS*.

* **Beta** (https://beta.simoc.space/)

  * hosted on a private server
  * intended for testing/experimenting
  * uses docker-compose

* **NGS** (https://ngs.simoc.space/)

  * hosted on GCP (Google Cloud Platform)
  * sponsored by National Geographic
  * uses kubernetes

Testing on Beta is recommended before deploying on NGS.


How to deploy
=============

While the deployment for both locations is automated through *GitHub
Actions*, it must be triggered manually.

In order to deploy:

1. go to https://github.com/overthesun/simoc/actions (you might need
   privileges)
2. select either the "Publish to Beta" or the "Publish to NGS" workflow
   on the left.
3. click on "Run workflow" on the right and specify the frontend and
   backend branches
4. click on the green "Run workflow" button to start the deployment
5. wait until the deployment is completed and make sure that beta/NGS
   have been updated successfully

The branch you specify in step 3 can be:

* a named branch (such as `master`)
* a pull request, by specifying :samp:`refs/pull/{NUM}/head`
  (where *NUM* is the PR number)
* a specific commit ID

`master` is considered the stable branch for both the `simoc` and
`simoc-web` repository, and generally only `master` should be
deployed on NGS.


.. note::

    For more informations regarding the initial GCP configuration
    and deployment, see: :doc:`gcp-deployment`


Workflow files
==============

The available workflows are defined by files listed at
https://github.com/overthesun/simoc/tree/master/.github/workflows.

While the two workflows are mostly similar, there are a few differences
(e.g. the way the containers are started).  Please refer to content of
the files for more information.
