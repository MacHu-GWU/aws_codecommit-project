# -*- coding: utf-8 -*-

"""
Better codecommit boto3 client
"""

import typing as T
import dataclasses
from typing import Optional, Tuple
from .boto_ses import cc_client


@dataclasses.dataclass
class Commit:
    commit_id: str = dataclasses.field(default="")
    tree_id: str = dataclasses.field(default="")
    parent_commit_ids: T.List[str] = dataclasses.field(default_factory=list)
    author_name: str = dataclasses.field(default="")
    author_email: str = dataclasses.field(default="")
    author_date: str = dataclasses.field(default="")
    committer_name: str = dataclasses.field(default="")
    committer_email: str = dataclasses.field(default="")
    committer_date: str = dataclasses.field(default="")
    additional_data: str = dataclasses.field(default="")


def get_commit(
    cc_client,
    repo_name: str,
    commit_id: str,
) -> Commit:
    """
    Get commit details

    :param cc_client: boto3.client("codecommit") object
    :param repo_name: CodeCommit repository name
    :param commit_id:
    :return:
    """
    res = cc_client.get_commit(
        repositoryName=repo_name,
        commitId=commit_id,
    )
    commit_dict = res["commit"]
    return Commit(
        commit_id=commit_dict.get("commitId", ""),
        tree_id=commit_dict.get("treeId", ""),
        parent_commit_ids=commit_dict.get("parents", []),
        author_name=commit_dict.get("author", {}).get("name", ""),
        author_email=commit_dict.get("author", {}).get("email", ""),
        author_date=commit_dict.get("author", {}).get("date", ""),
        committer_name=commit_dict.get("committer", {}).get("name", ""),
        committer_email=commit_dict.get("committer", {}).get("email", ""),
        committer_date=commit_dict.get("committer", {}).get("date", ""),
        additional_data=commit_dict.get("additionalData", ""),
    )


def get_branch_last_commit_id(
    cc_client,
    repo_name: str,
    branch_name: str,
) -> str:
    """
    See function name.

    :param repo_name: CodeCommit repository name
    :param branch_name: git branch name

    :return:
    """
    res = cc_client.get_branch(
        repositoryName=repo_name,
        branchName=branch_name,
    )
    return res["branch"]["commitId"]


def commit_file(
    repo_name: str,
    branch_name: str,
    file_content: bytes,
    file_path: str,
    commit_message: str,
    author_name: str,
    author_email: str,
    skip_if_no_change: bool = True,
) -> Optional[str]:  # pragma: no cover
    """
    Wrapper around boto3 CodeCommit client ``put_file`` method.

    Log some info and handle error.

    :return: the commit id of this action, could return None if failed
    """
    last_commit_id = get_last_commit_id_of_branch(repo_name, branch_name)
    try:
        res = cc_client.put_file(
            repositoryName=repo_name,
            branchName=branch_name,
            fileContent=file_content,
            filePath=file_path,
            fileMode="NORMAL",
            parentCommitId=last_commit_id,
            commitMessage=commit_message,
            name=author_name,
            email=author_email,
        )
        commit_id = res["commitId"]
        return commit_id
    except Exception as e:
        if skip_if_no_change:
            # file not changed skip commit
            if "SameFileContentException" in e.__class__.__name__:
                return None
        raise e


def get_text_file_content(
    repo_name: str,
    commit_id: str,
    file_path: str,
) -> str:
    """
    Get text file content from CodeCommit repo.
    """
    res = cc_client.get_file(
        repositoryName=repo_name,
        commitSpecifier=commit_id,
        filePath=file_path,
    )
    return res["fileContent"].decode("utf-8")


def post_comment_for_pull_request(
    repo_name: str,
    pr_id: str,
    before_commit_id: str,
    after_commit_id: str,
    content: str,
) -> str:
    """
    Put a comment in CodeCommit Pull Request activity view.
    """
    res = cc_client.post_comment_for_pull_request(
        pullRequestId=pr_id,
        repositoryName=repo_name,
        beforeCommitId=before_commit_id,
        afterCommitId=after_commit_id,
        content=content,
    )
    return res["comment"]["commentId"]


def update_comment(comment_id: str, content: str):  # pragma: no cover
    """
    Update an existing comment.
    """
    cc_client.update_comment(
        commentId=comment_id,
        content=content,
    )


def reply_comment(
    comment_id: str,
    content: str,
) -> str:  # pragma: no cover
    """
    Reply to comment
    """
    res = cc_client.post_comment_reply(
        inReplyTo=comment_id,
        content=content,
    )
    return res["comment"]["commentId"]
