# -*- coding: utf-8 -*-

import pytest
import typing as T
from aws_codecommit.semantic_branch import (
    is_main_branch,
    is_develop_branch,
    is_feature_branch,
    is_build_branch,
    is_doc_branch,
    is_fix_branch,
    is_release_branch,
)


@pytest.mark.parametrize(
    "branch,func,flag",
    [
        ("main", is_main_branch, True),
        ("master", is_main_branch, True),
        ("Dev", is_develop_branch, True),
        ("Develop", is_develop_branch, True),
        ("Feat", is_feature_branch, True),
        ("Feature", is_feature_branch, True),
        ("build", is_build_branch, True),
        ("doc", is_doc_branch, True),
        ("fix", is_fix_branch, True),
        ("rls", is_release_branch, True),
        ("release", is_release_branch, True),
    ],
)
def test_is_certain_semantic_branch(
    branch: str,
    func: T.Callable,
    flag: bool,
):
    assert func(branch) is flag


if __name__ == "__main__":
    from aws_codecommit.tests import run_cov_test

    run_cov_test(__file__, "aws_codecommit.semantic_branch", preview=False)
