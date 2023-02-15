# -*- coding: utf-8 -*-

"""
Semantic branch is a git branch naming convention to indicate what you are
trying to do on the git branch. Also, CI system can use branch name to
figure out what to do.
"""

import typing as T
import enum


class SemanticBranchEnum(str, enum.Enum):
    """
    Semantic branch name enumeration.
    """
    main = "main"
    master = "master"

    # based on purpose
    feat = "feat"
    feature = "feature"
    build = "build"
    doc = "doc"
    fix = "fix"
    hotfix = "hotfix"
    rls = "rls"
    release = "release"
    clean = "clean"
    cleanup = "cleanup"

    # based on environment
    dev = "dev"
    develop = "develop"
    test = "test"
    int = "int"
    stage = "stage"
    staging = "staging"
    qa = "qa"
    preprod = "preprod"
    prod = "prod"
    blue = "blue"
    green = "green"


def is_certain_semantic_branch(name: str, words: T.List[str]) -> bool:
    """
    Test if a branch name meet certain semantic rules.

    Below is an example to check if the branch name start with the keyword "feature"::

        >>> is_certain_semantic_branch(
        ...     name="feature/add-this-feature",
        ...     stub=["feat", "feature"],
        ... )
        True

    :param name: branch name
    :param words: semantic words

    :return: a boolean value
    """
    name = name.lower().strip()
    name = name.split("/")[0]
    words = set([word.lower().strip() for word in words])
    return name in words


def is_main_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.main,
            SemanticBranchEnum.master,
        ],
    )


def is_feature_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.feat,
            SemanticBranchEnum.feature,
        ],
    )


def is_build_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.build,
        ],
    )


def is_doc_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.doc,
        ],
    )


def is_fix_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.fix,
        ],
    )


def is_release_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.rls,
            SemanticBranchEnum.release,
        ],
    )


def is_cleanup_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.clean,
            SemanticBranchEnum.cleanup,
        ],
    )


def is_develop_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.dev,
            SemanticBranchEnum.develop,
        ],
    )


def is_test_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.test,
        ],
    )


def is_int_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.int,
        ],
    )


def is_staging_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.stage,
            SemanticBranchEnum.staging,
        ],
    )


def is_qa_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.qa,
        ],
    )


def is_preprod_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.preprod,
        ],
    )


def is_prod_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.prod,
        ],
    )


def is_blue_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.blue,
        ],
    )


def is_green_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.green,
        ],
    )
