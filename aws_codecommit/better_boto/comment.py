# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from datetime import datetime

from boto_session_manager import BotoSesManager, AwsServiceEnum

from .arg import NOTHING, resolve_kwargs


@dataclasses.dataclass
class Comment:
    """
    Data model of a CodeCommit comment.
    """
    comment_id: str = dataclasses.field(default="")
    content: str = dataclasses.field(default="")
    in_reply_to: T.Optional[str] = dataclasses.field(default=None)
    creation_date: T.Optional[datetime] = dataclasses.field(default=None)
    last_modified_date: T.Optional[datetime] = dataclasses.field(default=None)
    author_arn: T.Optional[str] = dataclasses.field(default=None)
    deleted: T.Optional[bool] = dataclasses.field(default=None)
    client_request_token: T.Optional[str] = dataclasses.field(default=None)

    @classmethod
    def from_dict(cls, dct: dict) -> "Comment":
        """
        Note: this is not a public API
        """
        return cls(
            comment_id=dct.get("commentId"),
            content=dct.get("content"),
            in_reply_to=dct.get("inReplyTo"),
            creation_date=dct.get("creationDate"),
            last_modified_date=dct.get("lastModifiedDate"),
            author_arn=dct.get("authorArn"),
            deleted=dct.get("deleted"),
            client_request_token=dct.get("clientRequestToken"),
        )


def get_comment(
    bsm: BotoSesManager,
    comment_id: str,
) -> Comment:
    """
    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_comment

    :param bsm:
    :param comment_id:
    :return:
    """
    res = bsm.codecommit_client.get_comment(commentId=comment_id)
    return Comment.from_dict(res["comment"])


def post_comment_for_compared_commit(
    bsm: BotoSesManager,
    repo_name: str,
    before_commit_id: str,
    after_commit_id: str,
    content: str,
    location: T.Optional[dict] = NOTHING,
    client_request_token: T.Optional[dict] = NOTHING,
) -> Comment:
    """
    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.post_comment_for_compared_commit

    :param bsm:
    :param repo_name:
    :param before_commit_id:
    :param after_commit_id:
    :param content:
    :param location:
    :param client_request_token:
    :return:
    """
    kwargs = resolve_kwargs(
        _mapper=dict(
            repo_name="repositoryName",
            before_commit_id="beforeCommitId",
            after_commit_id="afterCommitId",
            content="content",
            location="location",
            client_request_token="clientRequestToken",
        ),
        repo_name=repo_name,
        before_commit_id=before_commit_id,
        after_commit_id=after_commit_id,
        content=content,
        location=location,
        client_request_token=client_request_token,
    )
    res = bsm.codecommit_client.post_comment_for_compared_commit(**kwargs)
    return Comment.from_dict(res["comment"])


def post_comment_for_pull_request(
    bsm: BotoSesManager,
    pr_id: str,
    repo_name: str,
    before_commit_id: str,
    after_commit_id: str,
    content: str,
    location: T.Optional[dict] = NOTHING,
    client_request_token: T.Optional[dict] = NOTHING,
) -> Comment:
    """
    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.post_comment_for_pull_request

    :param bsm:
    :param pr_id:
    :param repo_name:
    :param before_commit_id:
    :param after_commit_id:
    :param content:
    :param location:
    :param client_request_token:
    :return:
    """
    kwargs = resolve_kwargs(
        _mapper=dict(
            pr_id="pullRequestId",
            repo_name="repositoryName",
            before_commit_id="beforeCommitId",
            after_commit_id="afterCommitId",
            content="content",
            location="location",
            client_request_token="clientRequestToken",
        ),
        pr_id=pr_id,
        repo_name=repo_name,
        before_commit_id=before_commit_id,
        after_commit_id=after_commit_id,
        content=content,
        location=location,
        client_request_token=client_request_token,
    )
    res = bsm.codecommit_client.post_comment_for_pull_request(**kwargs)
    return Comment.from_dict(res["comment"])


def post_comment_reply(
    bsm: BotoSesManager,
    in_reply_to: str,
    content: str,
    client_request_token: T.Optional[dict] = NOTHING,
) -> Comment:
    """
    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.post_comment_reply

    :return:
    """
    kwargs = resolve_kwargs(
        _mapper=dict(
            in_reply_to="inReplyTo",
            content="content",
            client_request_token="clientRequestToken",
        ),
        in_reply_to=in_reply_to,
        content=content,
        client_request_token=client_request_token,
    )
    res = bsm.codecommit_client.post_comment_reply(**kwargs)
    return Comment.from_dict(res["comment"])


def update_comment(
    bsm: BotoSesManager,
    comment_id: str,
    content: str,
) -> Comment:
    """
    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.update_comment

    :param bsm:
    :param comment_id:
    :param content:
    :return:
    """
    res = bsm.codecommit_client.update_comment(
        commentId=comment_id,
        content=content,
    )
    return Comment.from_dict(res["comment"])


class CommentThread:
    def __init__(self, bsm: BotoSesManager):
        self.bsm = bsm
        self.comment: T.Optional[Comment] = None
        self.reply_comment_list: T.List[Comment] = list()

    def post_comment(
        self,
        repo_name: str,
        before_commit_id: str,
        after_commit_id: str,
        content: str,
        pr_id: T.Optional[str] = NOTHING,
        location: T.Optional[dict] = NOTHING,
        client_request_token: T.Optional[dict] = NOTHING,
    ) -> Comment:
        if pr_id is NOTHING:
            method = post_comment_for_compared_commit
        else:
            method = post_comment_for_pull_request
        kwargs = resolve_kwargs(
            repo_name=repo_name,
            before_commit_id=before_commit_id,
            after_commit_id=after_commit_id,
            content=content,
            pr_id=pr_id,
            location=location,
            client_request_token=client_request_token,
        )

        self.comment = method(bsm=self.bsm, **kwargs)
        self.reply_comment_list.clear()
        return self.comment

    def reply(
        self,
        content: str,
        client_request_token: T.Optional[dict] = NOTHING,
    ) -> Comment:
        if self.comment is None:
            raise ValueError(
                "You have to call .post_comment() first to create a comment thread"
            )
        return post_comment_reply(
            bsm=self.bsm,
            in_reply_to=self.comment.comment_id,
            content=content,
            client_request_token=client_request_token,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.comment = None
        self.reply_comment_list.clear()


PullRequestCommentThread = CommentThread  # for backward compatibility
