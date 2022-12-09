# -*- coding: utf-8 -*-

"""
A simple regex parser to parse conventional commit message.
"""

import typing as T
import re
import enum
import string
import dataclasses

DELIMITERS = "!@#$%^&*()_+-=~`[{]}\\|;:'\",<.>/? \t\n"
CHARSET = string.ascii_letters


def tokenize(text: str) -> T.List[str]:
    cleaner_text = text
    for delimiter in DELIMITERS:
        cleaner_text = cleaner_text.replace(delimiter, " ")
    words = [word.strip() for word in cleaner_text.split(" ") if word.strip()]
    return words


def _get_subject_regex(_types: T.List[str]) -> T.Pattern:
    return re.compile(
        rf"^(?P<types>[\w ,]+)(?:\((?P<scope>[\w-]+)\))?(?P<breaking>!)?:[ \t]?(?P<description>.+)$"
    )


@dataclasses.dataclass
class ConventionalCommit:
    """
    Data container class for conventional commits message.
    """

    types: T.List[str]
    description: str = None
    scope: T.Optional[str] = None
    breaking: T.Optional[str] = None


class ConventionalCommitParser:
    """
    The customizable parser class. It tries to parse from
    ``type1, type2 (scope): {description}

    :param types: the list of conventional commit type you want to monitor
    """

    def __init__(self, types: T.List[str]):
        self.types = [type_.lower().strip() for type_ in types]
        self.subject_regex = _get_subject_regex(types)

    def extract_subject(self, msg: str) -> str:
        """
        Extract the subject line.
        """
        return msg.split("\n")[0].strip()

    def extract_commit(self, subject: str) -> ConventionalCommit:
        """
        Extract conventional commit object from the subject.
        """
        match = self.subject_regex.match(subject)
        types = [
            word.strip()
            for word in match["types"].split(",")
            if word.strip() in self.types
        ]

        # Debug only
        # print(match)
        # print([match["types"],])
        # print([match["description"], ])
        # print([match["scope"], ])
        # print([match["breaking"], ])

        return ConventionalCommit(
            types=types,
            description=match["description"],
            scope=match["scope"],
            breaking=match["breaking"],
        )

    def parse_message(self, commit_message: str) -> T.Optional[ConventionalCommit]:
        try:
            return self.extract_commit(self.extract_subject(commit_message))
        except Exception as e:
            return None


class SemanticCommitEnum(enum.Enum):
    """
    Semantic commit message can help CI to determine what you want to do.

    It is a good way to allow developer controls the CI behavior with small
    effort.
    """

    chore = "chore"  # house cleaning, do nothing
    feat = "feat"  # new feature
    feature = "feature"  # new feature
    fix = "fix"  # fix something
    doc = "doc"  # documentation
    test = "test"  # run all test
    utest = "utest"  # run unit test
    itest = "itest"  # run integration test
    ltest = "ltest"  # run load test
    build = "build"  # build artifacts
    pub = "pub"  # publish artifacts
    publish = "publish"  # publish artifacts
    rls = "rls"  # release
    release = "release"  # release

    @classmethod
    def to_str_list(cls) -> T.List[str]:
        return [e.value for e in cls]

    @classmethod
    def to_mapper(cls) -> T.Dict[str, "SemanticCommitEnum"]:
        return {e.name: e for e in cls}


semantic_commit_mapper = SemanticCommitEnum.to_mapper()


default_parser = ConventionalCommitParser(types=SemanticCommitEnum.to_str_list())


def is_certain_semantic_commit(
    commit_message: str,
    stub: T.Union[str, T.List[str]],
) -> bool:
    """

    :param commit_message:
    :param semantic_commit_stub:
    :return:
    """
    commit = default_parser.parse_message(commit_message)
    if commit is None:
        return False
    if isinstance(stub, str):
        stub_set = {
            stub,
        }
    else:
        stub_set = set(stub)
    return len(set(commit.types).intersection(stub_set)) > 0


def is_feat_commit(commit_message: str) -> bool:
    return is_certain_semantic_commit(
        commit_message,
        [SemanticCommitEnum.feat.value, SemanticCommitEnum.feature.value],
    )


def is_fix_commit(commit_message: str) -> bool:
    return is_certain_semantic_commit(
        commit_message,
        SemanticCommitEnum.fix.value,
    )


def is_doc_commit(commit_message: str) -> bool:
    return is_certain_semantic_commit(
        commit_message,
        SemanticCommitEnum.doc.value,
    )


def is_test_commit(commit_message: str) -> bool:
    return is_certain_semantic_commit(
        commit_message, [
            SemanticCommitEnum.test.value,
            SemanticCommitEnum.utest.value,
            SemanticCommitEnum.itest.value,
            SemanticCommitEnum.ltest.value,
        ]
    )


def is_utest_commit(commit_message: str) -> bool:
    return is_certain_semantic_commit(
        commit_message, SemanticCommitEnum.utest.value
    )


def is_itest_commit(commit_message: str) -> bool:
    return is_certain_semantic_commit(
        commit_message,
        SemanticCommitEnum.itest.value,
    )


def is_ltest_commit(commit_message: str) -> bool:
    return is_certain_semantic_commit(
        commit_message,
        SemanticCommitEnum.ltest.value,
    )


def is_build_commit(commit_message: str) -> bool:
    return is_certain_semantic_commit(
        commit_message,
        SemanticCommitEnum.build.value,
    )


def is_publish_commit(commit_message: str) -> bool:
    return is_certain_semantic_commit(
        commit_message,
        [SemanticCommitEnum.pub.value, SemanticCommitEnum.publish.value],
    )


def is_release_commit(commit_message: str) -> bool:
    return is_certain_semantic_commit(
        commit_message,
        [SemanticCommitEnum.rls.value, SemanticCommitEnum.release.value],
    )
