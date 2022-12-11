# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx


def test():
    import aws_codecommit

    _ = aws_codecommit.CodeCommitEvent
    _ = aws_codecommit.SemanticBranchEnum
    _ = aws_codecommit.is_certain_semantic_branch
    _ = aws_codecommit.SemanticCommitEnum
    _ = aws_codecommit.ConventionalCommitParser
    _ = aws_codecommit.default_parser
    _ = aws_codecommit.is_certain_semantic_commit

    _ = aws_codecommit.console

    _ = aws_codecommit.console.browse_commit
    _ = aws_codecommit.console.browse_code
    _ = aws_codecommit.console.browse_pr
    _ = aws_codecommit.console.browse_file

    _ = aws_codecommit.better_boto.Comment
    _ = aws_codecommit.better_boto.get_comment
    _ = aws_codecommit.better_boto.post_comment_for_compared_commit
    _ = aws_codecommit.better_boto.post_comment_for_pull_request
    _ = aws_codecommit.better_boto.post_comment_reply
    _ = aws_codecommit.better_boto.update_comment
    _ = aws_codecommit.better_boto.PullRequestCommentThread
    _ = aws_codecommit.better_boto.CommentThread
    _ = aws_codecommit.better_boto.Commit
    _ = aws_codecommit.better_boto.get_commit
    _ = aws_codecommit.better_boto.get_branch_last_commit_id
    _ = aws_codecommit.better_boto.Commit
    _ = aws_codecommit.better_boto.create_commit
    _ = aws_codecommit.better_boto.put_file
    _ = aws_codecommit.better_boto.PullRequest
    _ = aws_codecommit.better_boto.PulLRequestTarget
    _ = aws_codecommit.better_boto.get_pull_request
    _ = aws_codecommit.better_boto.File
    _ = aws_codecommit.better_boto.get_file


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
