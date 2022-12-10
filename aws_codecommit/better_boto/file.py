# -*- coding: utf-8 -*-

import typing as T
import base64
import dataclasses

from boto_session_manager import BotoSesManager, AwsServiceEnum


@dataclasses.dataclass
class File:
    commit_id: str = dataclasses.field()
    blob_id: str = dataclasses.field()
    file_path: str = dataclasses.field()
    file_mode: str = dataclasses.field()
    file_size: str = dataclasses.field()
    file_content: bytes = dataclasses.field()

    @property
    def binary(self) -> bytes:
        return self.file_content

    def get_text(self, encoding="utf-8") -> str:
        return self.binary.decode(encoding)

    @classmethod
    def from_dict(cls, dct: dict) -> "File":
        return cls(
            commit_id=dct["commitId"],
            blob_id=dct["blobId"],
            file_path=dct["filePath"],
            file_mode=dct["fileMode"],
            file_size=dct["fileSize"],
            file_content=dct["fileContent"],
        )


def get_file(
    bsm: BotoSesManager,
    repo_name: str,
    file_path: str,
    commit_id: T.Optional[str] = None,
    branch: T.Optional[str] = None,
    tag: T.Optional[str] = None,
    ref: T.Optional[str] = None,
):
    "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_file"
    flag_count = sum(
        [
            bool(commit_id),
            bool(branch),
            bool(tag),
            bool(ref),
        ]
    )
    if flag_count > 1:
        raise ValueError
    kwargs = dict(
        repositoryName=repo_name,
        filePath=file_path,
    )
    if flag_count == 0:
        pass
    elif commit_id:
        kwargs["commitSpecifier"] = commit_id
    elif branch:
        kwargs["commitSpecifier"] = branch
    elif tag:
        kwargs["commitSpecifier"] = tag
    elif ref:
        kwargs["commitSpecifier"] = ref
    else:  # pragma: no cover
        raise NotImplementedError

    res = bsm.get_client(AwsServiceEnum.CodeCommit).get_file(**kwargs)

    return File.from_dict(res)
