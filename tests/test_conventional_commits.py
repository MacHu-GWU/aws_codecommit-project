# -*- coding: utf-8 -*-

import pytest
import typing as T
from aws_codecommit.conventional_commits import (
    tokenize,
    ConventionalCommit,
    parser,
    is_feat_commit,
    is_fix_commit,
    is_doc_commit,
    is_utest_commit,
    is_itest_commit,
    is_ltest_commit,
    is_build_commit,
    is_publish_commit,
    is_release_commit,
)


@pytest.mark.parametrize(
    "before,after",
    [
        ("a, b, c", ["a", "b", "c"]),
        ("a, b: c d e", ["a", "b", "c", "d", "e"]),
    ],
)
def test_tokenize(before: str, after: T.List[str]):
    assert tokenize(before) == after


@pytest.mark.parametrize(
    "msg,commit,is_test_pairs",
    [
        (
            (
                "feat, build(STORY-001): add validator\n"
                "We have done the following\n"
                "\n"
                "1. first\n"
                "2. Second\n"
                "3. Third\n"
            ),
            ConventionalCommit(
                types=["feat", "build"],
                description="add validator",
                scope="STORY-001",
                breaking=None,
            ),
            [
                (is_feat_commit, True),
            ],
        ),
        # No Scope
        (
            (
                "fix: be able to handle negative value\n"
                "see ``def calculate()`` function\n"
            ),
            ConventionalCommit(
                types=[
                    "fix",
                ],
                description="be able to handle negative value",
                scope=None,
                breaking=None,
            ),
            [
                (is_fix_commit, True),
            ],
        ),
        # No space after ``:``
        (
            (
                "fix:be able to handle negative value\n"
                "see ``def calculate()`` function\n"
            ),
            ConventionalCommit(
                types=[
                    "fix",
                ],
                description="be able to handle negative value",
                scope=None,
                breaking=None,
            ),
            [
                (is_fix_commit, True),
            ],
        ),
        # has breaking
        (
            (
                "fix (API)!: no longer support Python3.7\n"
                "see ``def calculate()`` function\n"
            ),
            ConventionalCommit(
                types=[
                    "fix",
                ],
                description="no longer support Python3.7",
                scope="API",
                breaking="!",
            ),
            [
                (is_fix_commit, True),
            ],
        ),
    ],
)
def test_parse_message(
    msg: str,
    commit: ConventionalCommit,
    is_test_pairs: T.List[T.Tuple[T.Callable, bool]],
):
    assert parser.parse_message(msg) == commit
    for func, flag in is_test_pairs:
        assert func(msg) is flag


if __name__ == "__main__":
    from aws_codecommit.tests import run_cov_test

    run_cov_test(__file__, "aws_codecommit.conventional_commits")
