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

    _ = aws_codecommit.better_boto
    _ = aws_codecommit.console


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
