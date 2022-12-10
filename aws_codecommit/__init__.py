# -*- coding: utf-8 -*-

"""
empower AWS CodeCommit.
"""


from ._version import __version__

__short_description__ = "empower AWS CodeCommit"
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"


try:
    from .notification import (
        CodeCommitEvent,
    )
    from .semantic_branch import (
        SemanticBranchEnum,
        is_certain_semantic_branch,
    )
    from .conventional_commits import (
        SemanticCommitEnum,
        ConventionalCommitParser,
        default_parser,
        is_certain_semantic_commit,
    )
    from .console import (
        browse_code,
        browse_pr,
    )
    from . import better_boto, console
except ImportError as e: # pragma: no cover
    pass