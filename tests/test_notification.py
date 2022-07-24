# -*- coding: utf-8 -*-

import pytest

from typing import List
import re
import json
from pathlib import Path
from unittest.mock import patch, PropertyMock

import aws_codecommit.notification
from aws_codecommit.notification import (
    CodeCommitEventTypeEnum,
    CodeCommitEvent,
    SemanticCommitEnum,
    parse_commit_message,
)

CCEventTypeEnum = CodeCommitEventTypeEnum
CCE = CodeCommitEvent


def strip_comment_line_with_symbol(line, start):
    """
    Strip comments from line string.
    """
    parts = line.split(start)
    counts = [len(re.findall(r'(?:^|[^"\\]|(?:\\\\|\\")+)(")', part)) for part in parts]
    total = 0
    for nr, count in enumerate(counts):
        total += count
        if total % 2 == 0:
            return start.join(parts[: nr + 1]).rstrip()
    else:  # pragma: no cover
        return line.rstrip()


def strip_comments(string, comment_symbols=frozenset(("#", "//"))):
    """
    Strip comments from json string.
    :param string: A string containing json with comments started by comment_symbols.
    :param comment_symbols: Iterable of symbols that start a line comment (default # or //).
    :return: The string with the comments removed.
    """
    lines = string.splitlines()
    for k in range(len(lines)):
        for symbol in comment_symbols:
            lines[k] = strip_comment_line_with_symbol(lines[k], start=symbol)
    return "\n".join(lines)


dir_codecommit_events = Path(__file__).absolute().parent / "events"


def read_json(file: str) -> dict:
    return json.loads(strip_comments(Path(file).read_text()))


def read_cc_event(fname: str) -> CCE:
    return CCE.from_detail(
        read_json(f"{dir_codecommit_events / fname}")["detail"]
    )


class CCEventEnum:
    commit_to_master = read_cc_event("11-commit-to-master.json")
    branch_created = read_cc_event("21-branch-created.json")
    branch_updated = read_cc_event("22-branch-updated.json")
    branch_deleted = read_cc_event("23-branch-deleted.json")
    pull_request_created = read_cc_event("31-pull-request-created.json")
    pull_request_closed = read_cc_event("32-pull-request-closed.json")
    pull_request_updated = read_cc_event("33-pull-request-updated.json")
    pull_request_commit_merge_to_master = read_cc_event("34-pull-request-commit-merge-to-master.json")
    pull_request_merged = read_cc_event("35-pull-request-merged.json")
    comment_on_pull_request_specific_file = read_cc_event("41-comment-on-pull-request-specific-file.json")
    comment_on_pull_request_overall = read_cc_event("42-comment-on-pull-request-overall.json")
    reploy_to_comment = read_cc_event("43-reply-to-comment-message.json")
    approval = read_cc_event("44-approval.json")
    approval_rule_override = read_cc_event("45-approval-rule-override.json")


cc_event_list: List[CodeCommitEvent] = [
    v for k, v in CCEventEnum.__dict__.items() if not k.startswith("_")
]


def test_event_type():
    print(CCEventEnum.pull_request_commit_merge_to_master.is_commit_to_branch_from_merge)
    assert CCEventEnum.commit_to_master.is_commit_to_branch
    assert CCEventEnum.pull_request_commit_merge_to_master.is_commit_to_branch_from_merge
    assert CCEventEnum.branch_created.is_create_branch
    assert CCEventEnum.branch_updated.is_commit_to_branch
    assert CCEventEnum.branch_deleted.is_delete_branch
    assert CCEventEnum.pull_request_created.is_pr_created
    assert CCEventEnum.pull_request_closed.is_pr_closed
    assert CCEventEnum.pull_request_updated.is_pr_update
    assert CCEventEnum.pull_request_merged.is_pr_merged
    assert CCEventEnum.comment_on_pull_request_specific_file.is_comment_on_pr_created
    assert CCEventEnum.comment_on_pull_request_overall.is_comment_on_pr_created
    assert CCEventEnum.reploy_to_comment.is_reply_to_comment
    assert CCEventEnum.approval.is_approve_pr
    assert CCEventEnum.approval_rule_override.is_approve_rule_override


def test_properties():
    for cc_event in cc_event_list:
        assert cc_event.repo_name is not None

    assert CCEventEnum.pull_request_created.is_pr
    assert CCEventEnum.pull_request_closed.is_pr
    assert CCEventEnum.pull_request_updated.is_pr
    assert CCEventEnum.pull_request_merged.is_pr

    assert CCEventEnum.pull_request_created.pr_id is not None
    assert CCEventEnum.pull_request_closed.pr_id is not None
    assert CCEventEnum.pull_request_updated.pr_id is not None
    assert CCEventEnum.pull_request_merged.pr_id is not None

    with pytest.raises(TypeError):
        assert CCEventEnum.commit_to_master.pr_id

    assert CCEventEnum.pull_request_created.is_pr_created_or_updated
    assert CCEventEnum.pull_request_updated.is_pr_created_or_updated

    assert CCEventEnum.pull_request_created.pr_is_open
    assert CCEventEnum.pull_request_updated.pr_is_open
    assert CCEventEnum.pull_request_closed.pr_is_open is False
    assert CCEventEnum.pull_request_merged.pr_is_open is False

    assert CCEventEnum.pull_request_created.pr_is_merged is False
    assert CCEventEnum.pull_request_updated.pr_is_merged is False
    assert CCEventEnum.pull_request_closed.pr_is_merged is False
    assert CCEventEnum.pull_request_merged.pr_is_merged

    assert CCEventEnum.pull_request_updated.source_branch is not None
    assert CCEventEnum.pull_request_updated.source_commit is not None
    assert CCEventEnum.pull_request_updated.target_branch is not None
    assert CCEventEnum.pull_request_updated.target_commit is not None

    assert CCEventEnum.commit_to_master.source_commit is not None
    assert CCEventEnum.commit_to_master.source_is_main_branch

    assert CCEventEnum.commit_to_master.target_commit is not None
    with pytest.raises(NotImplementedError):
        _ = CCEventEnum.commit_to_master.target_branch


def test_semantic_branch():
    # syntax sugar to make the code shorter
    def source_branch(value):
        return patch.object(
            CodeCommitEvent,
            "source_branch",
            return_value=value,
            new_callable=PropertyMock,
        )

    def target_branch(value):
        return patch.object(
            CodeCommitEvent,
            "target_branch",
            return_value=value,
            new_callable=PropertyMock,
        )

    def new_event():
        return CCE()

    with source_branch("main"):
        assert new_event().is_main_branch
        assert new_event().is_develop_branch is False
        assert new_event().is_feature_branch is False
        assert new_event().is_release_branch is False
        assert new_event().is_hotfix_branch is False

    with source_branch("dev/"):
        assert new_event().is_main_branch is False
        assert new_event().is_develop_branch
        assert new_event().is_feature_branch is False
        assert new_event().is_release_branch is False
        assert new_event().is_hotfix_branch is False

    with source_branch("feat/"):
        assert new_event().is_main_branch is False
        assert new_event().is_develop_branch is False
        assert new_event().is_feature_branch
        assert new_event().is_release_branch is False
        assert new_event().is_hotfix_branch is False

    with source_branch("rls/"):
        assert new_event().is_main_branch is False
        assert new_event().is_develop_branch is False
        assert new_event().is_feature_branch is False
        assert new_event().is_release_branch
        assert new_event().is_hotfix_branch is False

    with source_branch("fix/"):
        assert new_event().is_main_branch is False
        assert new_event().is_develop_branch is False
        assert new_event().is_feature_branch is False
        assert new_event().is_release_branch is False
        assert new_event().is_hotfix_branch

    with target_branch("main"):
        assert new_event().target_is_main_branch

    with target_branch("dev"):
        assert new_event().target_is_develop_branch

    with target_branch("feat/"):
        assert new_event().target_is_feature_branch

    with target_branch("release/"):
        assert new_event().target_is_release_branch

    with target_branch("fix/"):
        assert new_event().target_is_hotfix_branch


def test_parse_commit_message():
    assert parse_commit_message("feat") == ["feat", ]
    assert parse_commit_message("feat: this is a feature") == ["feat", ]

    assert parse_commit_message("utest, itest") == ["utest", "itest"]
    assert parse_commit_message("utest, itest: update config") == ["utest", "itest"]

    assert parse_commit_message("not valid") == []


def test_semantic_commit_is_utest_commit():
    # syntax sugar to make the code shorter
    obj = CCE
    attr = "commit_message"

    def commit_message(value):
        return patch.object(
            obj,
            attr,
            return_value=value,
            new_callable=PropertyMock,
        )

    with commit_message("feat:"):
        assert CCEventEnum.commit_to_master.is_feat_commit

    with commit_message("utest:"):
        assert CCEventEnum.commit_to_master.is_utest_commit
        assert CCEventEnum.commit_to_master.is_test_commit

    with commit_message("itest:"):
        assert CCEventEnum.commit_to_master.is_itest_commit
        assert CCEventEnum.commit_to_master.is_test_commit

    with commit_message("ltest:"):
        assert CCEventEnum.commit_to_master.is_ltest_commit
        assert CCEventEnum.commit_to_master.is_test_commit

    with commit_message("build"):
        assert CCEventEnum.commit_to_master.is_build_commit

    with commit_message("pub"):
        assert CCEventEnum.commit_to_master.is_pub_commit

    with commit_message("rls"):
        assert CCEventEnum.commit_to_master.is_rls_commit

    with commit_message("fix"):
        assert CCEventEnum.commit_to_master.is_fix_commit

    with commit_message(
        "feat, utest, itest, ltest, build, pub, rls, fix: do everything"
    ):
        assert CCEventEnum.commit_to_master.is_feat_commit
        assert CCEventEnum.commit_to_master.is_utest_commit
        assert CCEventEnum.commit_to_master.is_itest_commit
        assert CCEventEnum.commit_to_master.is_ltest_commit
        assert CCEventEnum.commit_to_master.is_test_commit
        assert CCEventEnum.commit_to_master.is_build_commit
        assert CCEventEnum.commit_to_master.is_pub_commit
        assert CCEventEnum.commit_to_master.is_rls_commit
        assert CCEventEnum.commit_to_master.is_fix_commit


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
