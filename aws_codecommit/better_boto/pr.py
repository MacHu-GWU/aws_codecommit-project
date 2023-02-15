# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

from boto_session_manager import BotoSesManager, AwsServiceEnum

from ..console import browse_pr


@dataclasses.dataclass
class PulLRequestTarget:
    """
    Examples:

    If this event is about a PR that merge from 'dev' branch to 'main'.
    And the last commit in 'dev' is 'last-dev', and last commit in
    'main' is 'last-main'. Then:

    - ``self.src_ref`` is 'refs/heads/dev'
    - ``self.dst_ref`` is 'refs/heads/main'
    - ``self.src_commit`` is 'last-dev'
    - ``self.dst_commit`` is 'last-main'
    """
    repo_name: str = dataclasses.field()
    src_ref: str = dataclasses.field()
    dst_ref: str = dataclasses.field()
    src_commit: str = dataclasses.field()
    dst_commit: str = dataclasses.field()
    merge_base_commit: str = dataclasses.field()
    is_merged: T.Optional[bool] = dataclasses.field(default=None)
    merged_by: T.Optional[str] = dataclasses.field(default=None)
    merge_commit: T.Optional[str] = dataclasses.field(default=None)
    merge_option: T.Optional[str] = dataclasses.field(default=None)

    @classmethod
    def from_dict(cls, dct: dict) -> "PulLRequestTarget":
        return cls(
            repo_name=dct["repositoryName"],
            src_ref=dct["sourceReference"],
            dst_ref=dct["destinationReference"],
            src_commit=dct["sourceCommit"],
            dst_commit=dct["destinationCommit"],
            merge_base_commit=dct["mergeBase"],
            is_merged=dct.get("mergeMetadata", {}).get("isMerged"),
            merged_by=dct.get("mergeMetadata", {}).get("mergedBy"),
            merge_commit=dct.get("mergeMetadata", {}).get("mergeCommitId"),
            merge_option=dct.get("mergeMetadata", {}).get("mergeOption"),
        )


@dataclasses.dataclass
class PullRequest:
    """
    Data model of a Pull Request.
    """
    pr_id: str = dataclasses.field()
    title: str = dataclasses.field()
    pr_status: str = dataclasses.field()
    author_arn: str = dataclasses.field()
    revision_id: str = dataclasses.field()
    description: T.Optional[str] = dataclasses.field(default=None)
    last_active_date: T.Optional[datetime] = dataclasses.field(default=None)
    creation_date: T.Optional[datetime] = dataclasses.field(default=None)
    targets: T.List[PulLRequestTarget] = dataclasses.field(default_factory=list)
    client_request_token: T.Optional[str] = dataclasses.field(default=None)
    aws_region: T.Optional[str] = dataclasses.field(default=None)

    @classmethod
    def from_dict(cls, dct: dict) -> "PullRequest":
        """
        Note: this is not a public API
        """
        return cls(
            pr_id=dct["pullRequestId"],
            title=dct["title"],
            pr_status=dct["pullRequestStatus"],
            author_arn=dct["authorArn"],
            revision_id=dct["revisionId"],
            description=dct.get("description"),
            last_active_date=dct.get("lastActivityDate"),
            creation_date=dct.get("creationDate"),
            targets=[
                PulLRequestTarget.from_dict(d)
                for d in dct.get("pullRequestTargets", [])
            ],
            client_request_token=dct.get("clientRequestToken"),
        )

    @property
    def browse_console_url(self) -> str:
        return browse_pr(
            aws_region=self.aws_region,
            repo_name=self.targets[0].repo_name,
            pr_id=self.pr_id,
            detail_tab=True,
        )


def get_pull_request(bsm: BotoSesManager, pr_id: str) -> PullRequest:
    """
    Get Pull Request details.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_pull_request

    :param bsm:
    :param pr_id:
    :return:
    """
    res = bsm.codecommit_client.get_pull_request(
        pullRequestId=pr_id
    )
    pl = PullRequest.from_dict(res["pullRequest"])
    pl.aws_region = bsm.aws_region
    return pl
