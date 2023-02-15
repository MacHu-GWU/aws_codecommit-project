
.. .. image:: https://readthedocs.org/projects/aws_codecommit/badge/?version=latest
    :target: https://aws_codecommit.readthedocs.io/index.html
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/aws_codecommit-project/workflows/CI/badge.svg
    :target: https://github.com/MacHu-GWU/aws_codecommit-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/aws_codecommit-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/aws_codecommit-project

.. image:: https://img.shields.io/pypi/v/aws_codecommit.svg
    :target: https://pypi.python.org/pypi/aws_codecommit

.. image:: https://img.shields.io/pypi/l/aws_codecommit.svg
    :target: https://pypi.python.org/pypi/aws_codecommit

.. image:: https://img.shields.io/pypi/pyversions/aws_codecommit.svg
    :target: https://pypi.python.org/pypi/aws_codecommit

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/aws_codecommit-project

------

.. .. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://aws_codecommit.readthedocs.io/index.html

.. .. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://aws_codecommit.readthedocs.io/py-modindex.html

.. .. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
    :target: https://aws_codecommit.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/aws_codecommit-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/aws_codecommit-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/aws_codecommit-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/aws_codecommit#files


Welcome to ``aws_codecommit`` Documentation
==============================================================================
``aws_codecommit`` aim to extract more potential from AWS CodeCommit. ``aws_codecommit`` library is the foundation to bring `GitHub Action Trigger <https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows>`_, `CircleCI Workflow Trigger <https://circleci.com/docs/configuration-reference/#triggers>`_, `Jenkins Multi branch trigger <https://www.jenkins.io/doc/book/pipeline/multibranch/>`_, `GitLab Pipeline Trigger <https://docs.gitlab.com/ee/ci/pipelines/>`_ into AWS CodeCommit, and give you the flexibility to create more advanced custom trigger.

I created `one-click deployable, extentible CI/CD solution <https://github.com/MacHu-GWU/aws_ci_bot-project>`_ using AWS CodeCommit and AWS CodeBuild on top of ``aws_codecommit``.

Features:

- `Semantic commit parser <https://github.com/MacHu-GWU/aws_codecommit-project/blob/main/examples/Semantic-Commit-Parser.ipynb>`_
- `Semantic branch parser <https://github.com/MacHu-GWU/aws_codecommit-project/blob/main/examples/Semantic-Branch-Parser.ipynb>`_
- `Codecommit notification event parser <https://github.com/MacHu-GWU/aws_codecommit-project/blob/main/examples/codecommit-notification-event-parser.ipynb>`_
- better codecommit boto API


.. _install:

Install
------------------------------------------------------------------------------

``aws_codecommit`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install aws_codecommit

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade aws_codecommit
