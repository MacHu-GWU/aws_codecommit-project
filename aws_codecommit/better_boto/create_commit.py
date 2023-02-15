# -*- coding: utf-8 -*-

import typing as T

from boto_session_manager import BotoSesManager

from .arg import NOTHING, resolve_kwargs
from .commit import Commit


def create_commit(
    bsm: BotoSesManager,
    repo_name: str,
    branch_name: str,
    parent_commit_id: str,
    author_name: T.Optional[str] = NOTHING,
    author_email: T.Optional[str] = NOTHING,
    commit_message: T.Optional[str] = NOTHING,
    keep_empty_folders: T.Optional[bool] = NOTHING,
    put_files: T.Optional[T.List[dict]] = NOTHING,
    delete_files: T.Optional[T.List[dict]] = NOTHING,
    skip_if_no_change: bool = True,
) -> T.Optional[Commit]:  # pragma: no cover
    """
    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.create_commit

    :param bsm:
    :param repo_name:
    :param branch_name:
    :param parent_commit_id:
    :param author_name:
    :param author_email:
    :param commit_message:
    :param keep_empty_folders:
    :param put_files::

        [
            {
                "filePath": "string",
                "fileMode": "EXECUTABLE" | "NORMAL" | "SYMLINK",
                "fileContent": b"bytes" | "string",
                "sourceFile": {
                    "filePath": "string",
                    "isMove": True | False
                },
            },
        ]

    :param delete_files::

        [
            {
                "filePath": "string"
            },
        ]

    :param skip_if_no_change:
    :return:
    """
    kwargs = resolve_kwargs(
        _mapper=dict(
            repo_name="repositoryName",
            branch_name="branchName",
            parent_commit_id="parentCommitId",
            author_name="authorName",
            author_email="email",
            commit_message="commitMessage",
            keep_empty_folders="keepEmptyFolders",
            put_files="putFiles",
            delete_files="deleteFiles",
        ),
        repo_name=repo_name,
        branch_name=branch_name,
        parent_commit_id=parent_commit_id,
        author_name=author_name,
        author_email=author_email,
        commit_message=commit_message,
        keep_empty_folders=keep_empty_folders,
        put_files=put_files,
        delete_files=delete_files,
    )
    try:
        res = bsm.codecommit_client.create_commit(**kwargs)
        commit = Commit.from_dict(res)
        commit.repo_name = repo_name
        commit.aws_region = bsm.aws_region
        return commit
    except Exception as e:
        if skip_if_no_change:
            if "NoChangeException" in e.__class__.__name__:
                return None
            else:
                raise e
        else:
            raise e


def put_file(
    bsm: BotoSesManager,
    repo_name: str,
    branch_name: str,
    file_path: str,
    file_content: T.Union[str, bytes],
    file_mode: T.Optional[str] = NOTHING,
    parent_commit_id: T.Optional[str] = NOTHING,
    commit_message: T.Optional[str] = NOTHING,
    author_name: T.Optional[str] = NOTHING,
    author_email: T.Optional[str] = NOTHING,
    skip_if_no_change: bool = True,
) -> T.Optional[Commit]:
    """
    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.put_file

    :param bsm:
    :param repo_name:
    :param branch_name:
    :param file_content:
    :param file_path:
    :param file_mode:
    :param parent_commit_id:
    :param commit_message:
    :param author_name:
    :param author_email:
    :param skip_if_no_change:
    :return:
    """
    kwargs = resolve_kwargs(
        _mapper=dict(
            repo_name="repositoryName",
            branch_name="branchName",
            file_content="fileContent",
            file_path="filePath",
            file_mode="fileMode",
            parent_commit_id="parentCommitId",
            commit_message="commitMessage",
            author_name="name",
            author_email="email",
        ),
        repo_name=repo_name,
        branch_name=branch_name,
        file_content=file_content,
        file_path=file_path,
        file_mode=file_mode,
        parent_commit_id=parent_commit_id,
        commit_message=commit_message,
        author_name=author_name,
        author_email=author_email,
    )
    try:
        res = bsm.codecommit_client.put_file(**kwargs)
        commit = Commit.from_dict(res)
        commit.repo_name = repo_name
        commit.aws_region = bsm.aws_region
        return commit
    except Exception as e:
        if skip_if_no_change:
            if "SameFileContentException" in e.__class__.__name__:
                return None
            else:
                raise e
        else:
            raise e
