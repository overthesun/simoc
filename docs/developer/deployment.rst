==================
SIMOC's Deployment
==================

There are currently two available deployments of SIMOC: **NGS** and **beta**.

* **NGS** (https://ngs.simoc.space): official version, sponsored
  by National Geographic
* **Beta** (https://beta.simoc.space): intended for testing/experimenting

Testing on Beta is recommended before deploying on NGS.


How to deploy
=============

While the deployment for both locations is automated through *GitHub
Actions*, it must be triggered manually.

In order to deploy:

1. go to https://github.com/overthesun/simoc/actions (you might need
   privileges)
2. select the "Deploy SIMOC" workflow on the left
3. click on "Run workflow" on the right and specify the frontend and
   backend branches and the host from the dropdown
4. click on the green "Run workflow" button to start the deployment
5. wait until the deployment is completed and make sure that beta/NGS
   have been updated successfully

The branches you specify in step 3 can be:

* a named branch (such as ``master``)
* a pull request, by specifying :samp:`refs/pull/{NUM}/head`
  (where *NUM* is the PR number)
* a specific commit ID

``master`` is considered the stable branch for both the ``simoc`` and
``simoc-web`` repository, and generally only ``master`` should be
deployed on NGS.


Workflow files
==============

The current worflow and some legacy workflows are defined by files listed at
https://github.com/overthesun/simoc/tree/master/.github/workflows.
