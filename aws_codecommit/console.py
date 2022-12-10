# -*- coding: utf-8 -*-

"""
AWS Console URL builder
"""

import typing as T


def browse_code(
    aws_region: str,
    repo_name: str,
    branch: T.Optional[str] = None,
    commit_id: T.Optional[str] = None,
    tag: T.Optional[str] = None,
) -> str:
    if (
        sum(
            [
                bool(branch),
                bool(commit_id),
                bool(tag),
            ]
        )
        > 1
    ):
        raise ValueError

    if branch:
        return f"https://{aws_region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repo_name}/browse/refs/heads/{branch}?region={aws_region}"
    elif commit_id:
        return f"https://{aws_region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repo_name}/browse/{commit_id}?region={aws_region}"
    elif tag:
        return f"https://{aws_region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repo_name}/browse/refs/tags/{tag}?region={aws_region}"
    else:
        return f"https://{aws_region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repo_name}/browse?region={aws_region}"


def browse_pr(
    aws_region: str,
    repo_name: str,
    pr_id: str,
    detail_tab: T.Optional[bool] = None,
    activity_tab: T.Optional[bool] = None,
    changes_tab: T.Optional[bool] = None,
    commits_tab: T.Optional[bool] = None,
    approvals_tab: T.Optional[bool] = None,
):
    flag_count = sum(
        [
            bool(detail_tab),
            bool(activity_tab),
            bool(changes_tab),
            bool(commits_tab),
            bool(approvals_tab),
        ]
    )
    if flag_count > 1:
        raise ValueError

    if flag_count == 0:
        tab = "details"
    elif detail_tab:
        tab = "details"
    elif activity_tab:
        tab = "activity"
    elif changes_tab:
        tab = "changes"
    elif commits_tab:
        tab = "commits"
    elif approvals_tab:
        tab = "approvals"
    else:
        raise NotImplementedError

    return (
        f"https://{aws_region}.console.aws.amazon.com/codesuite/codecommit"
        f"/repositories/{repo_name}/pull-requests/{pr_id}"
        f"/{tab}?region={aws_region}"
    )


def browse_commit(
    aws_region: str,
    repo_name: str,
    commit_id: str,
) -> str:
    return (
        f"https://{aws_region}.console.aws.amazon.com/codesuite/codecommit"
        f"/repositories/{repo_name}/commit"
        f"/{commit_id}?region={aws_region}"
    )
