==============
Git Guidelines
==============

.. _repo-setup:

Repository setup
================

.. note::

    To access, fork, clone, and install SIMOC, you will also need access
    to the `SIMOC GitHub repository <https://github.com/overthesun/simoc>`_.

If you just want to have a local clone of the repository use::

    $ git clone git@github.com:overthesun/simoc.git

If you are also planning to contribute, fork the repo on GitHub and use::

    $ git clone git@github.com:<yourusername>/simoc.git

Add an ``upstream`` remote with::

    $ git remote add upstream git@github.com:overthesun/simoc.git

By doing this you can use ``origin`` to refer to your fork and
``upstream`` to refer to the main repository.  You can verify this
by running::

    $ git remote -v
    origin  git@github.com:<yourusername>/simoc.git (fetch)
    origin  git@github.com:<yourusername>/simoc.git (push)
    upstream  git@github.com:overthesun/simoc.git (fetch)
    upstream  git@github.com:overthesun/simoc.git (push)


Workflow
========

1. Update the ``master`` branch of your local copy using::

    git switch master
    git pull upstream master

2. Create a new branch from ``master`` using::

    git switch -c <name-of-the-branch>

3. Make changes and review, add, and commit them::

    git status           # check current branch and modified files
    git diff             # review changes
    git add -p           # review and add individual changes
    git commit -m '...'  # commit the changes

4. Push the changes to your fork::

    git push origin <name-of-the-branch>

5. Create a pull request (PR) against the upstream repo, either from
   the GitHub interface or by following the link that should appear
   after pushing.

6. Once the PR has been reviewed and merged, go back to step 1 to update
   your local clone, and delete the merged branch with::

    git branch -d <name-of-the-branch>

.. note::

    Commits should never be created or pushed directly on ``master``.
    A new branch and a PR should always be created.

.. note::

    On older versions of Git, the ``switch`` command is not available.
    Use ``git checkout -b <branch>`` to create a new branch and
    ``git checkout <branch>`` to switch to a different branch.


Pull Requests (PRs)
-------------------
Each pull request should be self-contained and address a single issue
(usually by either adding a feature or fixing a bug).  After a PR is
merged, the code should still run without errors.  Incomplete and
work-in-progress PRs shouldn't be merged, unless they are part of a
:ref:`Feature branch <feature-branches>`.

Each pull request can contain multiple commits.  It is possible
to add more commits to the PR by simply creating them in the branch
and pushing the changes to your fork with ``git push origin <branch>``.

PRs should include tests and documentation whenever possible.


Commits
-------
Commits should also be self-contained and address a single issue,
and can be used to break down an issue in smaller tasks that are
tackled separately.

Commits should not include unrelated changes (e.g. reformatting/linting
code other than the one that is being added/updated).

Try to limit the number of commits by using ``git status``,
``git diff``, and ``git add -p`` to review your changes carefully
before adding them and creating the commit.  Having a smaller number
of focused commit with a clear commit message makes the history easier
to navigate and understand.


Commit Messages
---------------
The commit message should be a short sentence, starting with a
capitalized word and ending with a period, that describes the change
being committed.  It's common to use an imperative verb at the beginning
of the message (e.g. ``'Add <feature>.'``, ``'Fix <bug>.'``,
``'Improve <something>.'``).

It's also possible to leave an empty line followed by one or more
paragraphs to explain the changes in detail.  If the commit addresses
a specific GitHub issues, adding the issue number is recommended.


.. _feature-branches:

Feature Branches
----------------

Feature branches can be used to develop complex features that require
multiple separate pull requests.  Once a feature branch is created,
other branches and PRs can be created from and merged into the feature
branch.

This makes it easier to develop and test the feature branch incrementally
without affecting the ``master`` branch and without creating a giant pull
request.  Once the feature is completed and tested, the whole branch can
be merged into ``master``.


Merge strategy
--------------
PRs are usually merged normally through the GitHub interface.  If the
commits included in the PR don't have meaningful messages or if there
is a lot of noise (e.g. several failed experiments, or many small
changes like typo fixes), a *squash merge* can be used instead.
