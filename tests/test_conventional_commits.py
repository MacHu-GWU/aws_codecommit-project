# -*- coding: utf-8 -*-

import os
import pytest
from typing import List
from aws_codecommit.conventional_commits import (
    tokenize, parse_commit, Commit
)


@pytest.mark.parametrize(
    "before,after",
    [
        ("a, b, c", ["a", "b", "c"]),
        ("a, b: c d e", ["a", "b", "c", "d", "e"]),
    ]
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
            Commit(
                types=["feat", "build"],
                description="add validator",
                scope="STORY-001",
                breaking=None,
            )
        ),
        # No Scope
        (
            (
                "fix: be able to handle negative value\n"
                "see ``def calculate()`` function\n"
            ),
            Commit(
                types=["fix", ],
                description="be able to handle negative value",
                scope=None,
                breaking=None,
            )
        ),
        # No space after ``:``
        (
            (
                "fix:be able to handle negative value\n"
                "see ``def calculate()`` function\n"
            ),
            Commit(
                types=["fix", ],
                description="be able to handle negative value",
                scope=None,
                breaking=None,
            )
        ),
        # has breaking
        (
            (
                "fix (API)!: no longer support Python3.7\n"
                "see ``def calculate()`` function\n"
            ),
            Commit(
                types=["fix", ],
                description="no longer support Python3.7",
                scope="API",
                breaking="!",
            )
        ),
    ]
)
def test_parse_commit(msg: str, commit: Commit):
    assert parse_commit(msg) == commit


if __name__ == "__main__":
    import sys
    import subprocess

    abspath = os.path.abspath(__file__)
    dir_project_root = os.path.dirname(abspath)
    for _ in range(10):
        if os.path.exists(os.path.join(dir_project_root, ".git")):
            break
        else:
            dir_project_root = os.path.dirname(dir_project_root)
    else:
        raise FileNotFoundError("cannot find project root dir!")
    dir_htmlcov = os.path.join(dir_project_root, "htmlcov")
    bin_pytest = os.path.join(os.path.dirname(sys.executable), "pytest")

    args = [
        bin_pytest,
        "-s", "--tb=native",
        f"--rootdir={dir_project_root}",
        "--cov=aws_codecommit.conventional_commits",
        "--cov-report", "term-missing",
        "--cov-report", f"html:{dir_htmlcov}",
        abspath,
    ]
    subprocess.run(args)
