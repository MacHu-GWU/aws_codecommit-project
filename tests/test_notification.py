# -*- coding: utf-8 -*-

import typing as T
import re
import json
import dataclasses
from pathlib import Path
from unittest.mock import patch, PropertyMock

from aws_codecommit.notification import (
    CodeCommitEventTypeEnum,
    CodeCommitEvent,
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
    return CCE.from_event(read_json(f"{dir_codecommit_events / fname}"))


class CCEventEnum:
    commit_to_master = read_cc_event("11-commit-to-master.json")
    branch_created = read_cc_event("21-branch-created.json")
    branch_updated = read_cc_event("22-branch-updated.json")
    branch_deleted = read_cc_event("23-branch-deleted.json")
    pull_request_created = read_cc_event("31-pull-request-created.json")
    pull_request_closed = read_cc_event("32-pull-request-closed.json")
    pull_request_updated = read_cc_event("33-pull-request-updated.json")
    pull_request_commit_merge_to_master = read_cc_event(
        "34-pull-request-commit-merge-to-master.json"
    )
    pull_request_merged = read_cc_event("35-pull-request-merged.json")
    comment_on_pull_request_specific_file = read_cc_event(
        "41-comment-on-pull-request-specific-file.json"
    )
    comment_on_pull_request_overall = read_cc_event(
        "42-comment-on-pull-request-overall.json"
    )
    reply_to_comment_pr_created = read_cc_event(
        "43-reply-to-comment-message-pr-created.json"
    )
    comment_on_pull_request_updated = read_cc_event(
        "44-comment-on-pull-request-updated.json"
    )
    comment_on_pull_request_merged = read_cc_event(
        "45-comment-on-pull-request-merged.json"
    )
    reply_to_comment_pr_updated = read_cc_event(
        "46-reply-to-comment-message-pr-updated.json"
    )
    approval = read_cc_event("51-approval.json")
    approval_rule_override = read_cc_event("52-approval-rule-override.json")


cc_event_list: T.List[CodeCommitEvent] = [
    v for k, v in CCEventEnum.__dict__.items() if not k.startswith("_")
]


def test_env_var_seder():
    for cc_event in cc_event_list:
        env_var = cc_event.to_env_var(prefix="CUSTOM_")
        cc_event1 = CodeCommitEvent.from_env_var(env_var, prefix="CUSTOM_")
        assert dataclasses.asdict(cc_event) == dataclasses.asdict(cc_event1)


def test_event_type():
    # positive case
    assert CCEventEnum.commit_to_master.is_commit_to_branch_event
    assert (
        CCEventEnum.pull_request_commit_merge_to_master.is_commit_to_branch_from_merge_event
    )
    assert CCEventEnum.branch_created.is_create_branch_event
    assert CCEventEnum.branch_updated.is_commit_to_branch_event
    assert CCEventEnum.branch_deleted.is_delete_branch_event
    assert CCEventEnum.pull_request_created.is_pr_created_event
    assert CCEventEnum.pull_request_closed.is_pr_closed_event
    assert CCEventEnum.pull_request_updated.is_pr_update_event
    assert CCEventEnum.pull_request_merged.is_pr_merged_event
    assert (
        CCEventEnum.comment_on_pull_request_specific_file.is_comment_on_pr_created_event
    )
    assert CCEventEnum.comment_on_pull_request_overall.is_comment_on_pr_created_event
    assert CCEventEnum.reply_to_comment_pr_created.is_reply_to_comment_event
    assert CCEventEnum.comment_on_pull_request_updated.is_comment_on_pr_updated_event
    assert CCEventEnum.comment_on_pull_request_merged.is_comment_on_pr_created_event
    assert CCEventEnum.reply_to_comment_pr_updated.is_reply_to_comment_event
    assert CCEventEnum.approval.is_approve_pr_event
    assert CCEventEnum.approval_rule_override.is_approve_rule_override_event

    # negative case
    assert CCEventEnum.pull_request_created.is_pr_closed_event is False
    assert CCEventEnum.pull_request_created.is_pr_update_event is False
    assert CCEventEnum.pull_request_created.is_pr_merged_event is False

    assert CCEventEnum.pull_request_closed.is_pr_created_event is False
    assert CCEventEnum.pull_request_closed.is_pr_update_event is False
    assert CCEventEnum.pull_request_closed.is_pr_merged_event is False

    assert CCEventEnum.pull_request_updated.is_pr_created_event is False
    assert CCEventEnum.pull_request_updated.is_pr_closed_event is False
    assert CCEventEnum.pull_request_updated.is_pr_merged_event is False

    assert CCEventEnum.pull_request_merged.is_pr_created_event is False
    assert CCEventEnum.pull_request_merged.is_pr_closed_event is False
    assert CCEventEnum.pull_request_merged.is_pr_update_event is False

    # event type enum is string
    assert type(CCEventEnum.pull_request_updated.event_type) is str
    assert CCEventEnum.pull_request_updated.event_type == CCEventTypeEnum.pr_updated
    assert (
        CCEventEnum.pull_request_updated.event_type == CCEventTypeEnum.pr_updated.value
    )


def test_properties():
    for cc_event in cc_event_list:
        assert cc_event.repo_name
        assert cc_event.aws_account_id
        assert cc_event.aws_region

    assert CCEventEnum.pull_request_created.is_pr_event
    assert CCEventEnum.pull_request_closed.is_pr_event
    assert CCEventEnum.pull_request_updated.is_pr_event
    assert CCEventEnum.pull_request_merged.is_pr_event

    assert CCEventEnum.pull_request_created.pr_id
    assert CCEventEnum.pull_request_closed.pr_id
    assert CCEventEnum.pull_request_updated.pr_id
    assert CCEventEnum.pull_request_merged.pr_id

    assert CCEventEnum.commit_to_master.pr_id == ""

    assert CCEventEnum.pull_request_created.is_pr_created_or_updated_event
    assert CCEventEnum.pull_request_updated.is_pr_created_or_updated_event

    assert CCEventEnum.pull_request_created.pr_is_open
    assert CCEventEnum.pull_request_updated.pr_is_open
    assert CCEventEnum.pull_request_closed.pr_is_open is False
    assert CCEventEnum.pull_request_merged.pr_is_open is False

    assert CCEventEnum.pull_request_created.pr_is_merged is False
    assert CCEventEnum.pull_request_updated.pr_is_merged is False
    assert CCEventEnum.pull_request_closed.pr_is_merged is False
    assert CCEventEnum.pull_request_merged.pr_is_merged

    assert CCEventEnum.pull_request_updated.source_branch
    assert CCEventEnum.pull_request_updated.source_commit
    assert CCEventEnum.pull_request_updated.target_branch
    assert CCEventEnum.pull_request_updated.target_commit

    assert CCEventEnum.commit_to_master.source_branch
    assert CCEventEnum.commit_to_master.source_commit
    assert CCEventEnum.commit_to_master.source_is_main_branch
    assert CCEventEnum.commit_to_master.target_commit
    assert CCEventEnum.commit_to_master.target_branch == ""

    assert CCEventEnum.commit_to_master.is_comment_event is False
    assert CCEventEnum.pull_request_created.is_comment_event is False
    assert CCEventEnum.approval.is_comment_event is False
    assert CCEventEnum.comment_on_pull_request_overall.is_comment_event
    assert CCEventEnum.comment_on_pull_request_specific_file.is_comment_event

    assert CCEventEnum.comment_on_pull_request_overall.source_branch == ""
    assert CCEventEnum.comment_on_pull_request_overall.source_commit
    assert CCEventEnum.comment_on_pull_request_overall.target_branch == ""
    assert CCEventEnum.comment_on_pull_request_overall.target_commit

    assert CCEventEnum.approval.source_branch
    assert CCEventEnum.approval.source_commit
    assert CCEventEnum.approval.target_branch
    assert CCEventEnum.approval.target_commit


def test_semantic_branch():
    # syntax sugar to make the code shorter
    def pull_request():
        return patch.object(
            CodeCommitEvent,
            "is_pr_event",
            return_value=True,
            new_callable=PropertyMock,
        )

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

    with pull_request():
        with target_branch("main"):
            with source_branch("dev/"):
                assert CCE().is_pr_from_develop_to_main
                assert CCE().is_pr_from_feature_to_main is False
                assert CCE().is_pr_from_hotfix_to_main is False

            with source_branch("feat/"):
                assert CCE().is_pr_from_develop_to_main is False
                assert CCE().is_pr_from_feature_to_main
                assert CCE().is_pr_from_hotfix_to_main is False

            with source_branch("fix/"):
                assert CCE().is_pr_from_develop_to_main is False
                assert CCE().is_pr_from_feature_to_main is False
                assert CCE().is_pr_from_hotfix_to_main


if __name__ == "__main__":
    from aws_codecommit.tests import run_cov_test

    run_cov_test(__file__, "aws_codecommit.notification")
