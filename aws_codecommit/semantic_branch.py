# -*- coding: utf-8 -*-

import typing as T
import enum


class SemanticBranchEnum(str, enum.Enum):
    main = "main"
    master = "master"
    dev = "dev"
    develop = "develop"
    feat = "feat"
    feature = "feature"
    build = "build"
    doc = "doc"
    fix = "fix"
    hotfix = "hotfix"
    rls = "rls"
    release = "release"


def is_certain_semantic_branch(name: str, words: T.List[str]) -> bool:
    """
    Test if a branch name meet certain semantic rules

    :param name: branch name
    :param words: semantic words
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


def is_develop_branch(name: str) -> bool:
    return is_certain_semantic_branch(
        name,
        [
            SemanticBranchEnum.dev,
            SemanticBranchEnum.develop,
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
