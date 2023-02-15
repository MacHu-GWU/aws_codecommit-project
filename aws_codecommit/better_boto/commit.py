# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from boto_session_manager import BotoSesManager
from ..console import browse_commit


@dataclasses.dataclass
class Commit:
    """
    Data model of a CodeCommit comment.
    """
    commit_id: str = dataclasses.field(default="")
    tree_id: str = dataclasses.field(default="")
    parent_commit_ids: T.List[str] = dataclasses.field(default_factory=list)
    message: T.Optional[str] = dataclasses.field(default="")
    author_name: str = dataclasses.field(default="")
    author_email: str = dataclasses.field(default="")
    author_date: str = dataclasses.field(default="")
    committer_name: str = dataclasses.field(default="")
    committer_email: str = dataclasses.field(default="")
    committer_date: str = dataclasses.field(default="")
    additional_data: str = dataclasses.field(default="")
    repo_name: str = dataclasses.field(default="")
    aws_region: str = dataclasses.field(default="")

    @classmethod
    def from_dict(cls, dct: dict) -> "Commit":
        """
        Note: this is not a public API
        """
        return cls(
            commit_id=dct.get("commitId", ""),
            tree_id=dct.get("treeId", ""),
            parent_commit_ids=dct.get("parents", []),
            message=dct.get("message", ""),
            author_name=dct.get("author", {}).get("name", ""),
            author_email=dct.get("author", {}).get("email", ""),
            author_date=dct.get("author", {}).get("date", ""),
            committer_name=dct.get("committer", {}).get("name", ""),
            committer_email=dct.get("committer", {}).get("email", ""),
            committer_date=dct.get("committer", {}).get("date", ""),
            additional_data=dct.get("additionalData", ""),
        )

    @property
    def browse_console_url(self) -> str:
        return browse_commit(
            aws_region=self.aws_region,
            repo_name=self.repo_name,
            commit_id=self.commit_id,
        )


def get_commit(
    bsm: BotoSesManager,
    repo_name: str,
    commit_id: str,
) -> Commit:
    """
    Get commit details.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_commit

    :param cc_client: boto3.client("codecommit") object
    :param repo_name: CodeCommit repository name
    :param commit_id:
    :return:
    """
    res = bsm.codecommit_client.get_commit(
        repositoryName=repo_name,
        commitId=commit_id,
    )
    commit = Commit.from_dict(res["commit"])
    commit.repo_name = repo_name
    commit.aws_region = bsm.aws_region
    return commit


def get_branch_last_commit_id(
    bsm: BotoSesManager,
    repo_name: str,
    branch_name: str,
) -> str:
    """
    See function name.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_branch

    :param repo_name: CodeCommit repository name
    :param branch_name: git branch name

    :return:
    """
    res = bsm.codecommit_client.get_branch(
        repositoryName=repo_name,
        branchName=branch_name,
    )
    return res["branch"]["commitId"]
