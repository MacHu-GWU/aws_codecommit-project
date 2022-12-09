# -*- coding: utf-8 -*-

import pytest
from typing import List
from aws_codecommit.conventional_commits import tokenize, ConventionalCommit, parser


@pytest.mark.parametrize(
    "before,after",
    [
        ("a, b, c", ["a", "b", "c"]),
        ("a, b: c d e", ["a", "b", "c", "d", "e"]),
    ],
)
def test_tokenize(before: str, after: List[str]):
    assert tokenize(before) == after


@pytest.mark.parametrize(
    "msg,commit",
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
        ),
    ],
)
def test_parse_message(msg: str, commit: ConventionalCommit):
    assert parser.parse_message(msg) == commit


if __name__ == "__main__":
    from aws_codecommit.tests import run_cov_test

    run_cov_test(__file__, "aws_codecommit.conventional_commits")
