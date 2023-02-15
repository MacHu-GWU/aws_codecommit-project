.. _release_history:

Release and Version History
==============================================================================


Backlog
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


1.4.1 (2023-02-15)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- now :class:`~aws_codecommit.conventional_commits.is_certain_semantic_commit` allow to use custom :class:`~aws_codecommit.conventional_commits.ConventionalCommitParser`

**Minor Improvements**

- add more common type to :class:`~aws_codecommit.semantic_branch.SemanticBranchEnum`
- add more common type to :class:`~aws_codecommit.conventional_commits.SemanticCommitEnum`


1.3.3 (2022-12-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Miscellaneous**

- the CodeCommitEvent.event_type should return a string, not a Enum object


1.3.2 (2022-12-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Miscellaneous**

- add a lot of function from better_boto to public API (forgot to add in 1.3.1)


1.3.1 (2022-12-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``aws_codecommit.CommentThread`` to the public API, it can do comment for both Pull Request and commits.

**Minor Improvements**

- add :func:`~aws_codecommit.console.browse_file` method

**Bugfixes**

- fix a bug that the ``PullRequest`` object doesn't have the right source and destination commit.

**Miscellaneous**

- more integration test for ``better_boto`` module


1.2.1 (2022-12-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Minor Improvements**

- add :func:`~aws_codecommit.console.browse_commit` method


1.1.2 (2022-12-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- fix a bug that ``get_commit`` didn't load the commit message into ``Commit`` object.


1.1.1 (2022-12-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``aws_codecommit.better_boto`` module, a objective oriented boto3.client("codecommit") API. I am actively adding more feature to it.
- add ``aws_codecommit.console`` module, a aws codecommit console url builder.


1.0.1 (2022-12-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First API stable release
- add the following API:
    - ``aws_codecommit.CodeCommitEvent``
    - ``aws_codecommit.SemanticBranchEnum``
    - ``aws_codecommit.is_certain_semantic_branch``
    - ``aws_codecommit.SemanticCommitEnum``
    - ``aws_codecommit.is_certain_semantic_commit``
    - ``aws_codecommit.ConventionalCommitParser``
    - ``aws_codecommit.default_parser``


0.0.7 (2022-08-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add ``conventional_commits`` parser module, but not used in the CI bot lambda handler.


0.0.6 (2022-07-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``is_pr_from_specific_branch_to_specific_branch`` method.
- add ``get_commit_message_and_committer`` function.


0.0.5 (2022-07-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add a few condition test functions
- Add aws account id, and aws region attribute to data model


0.0.4 (2022-07-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add AWS CodeCommit notification event data model
