# -*- coding: utf-8 -*-

"""
The core of CI/CD on AWS CodeCommit / CodeBuild.

You can create an AWS CodeCommit notification event rule, and send those events
to AWS SNS topic, then use an AWS Lambda function to subscript the SNS topic,
use this library to parse the data, and use if else condition to decide when
to trigger CI build job.

This solution requires >= Python3.8 because of the ``cached_property``
Since it is only used in the AWS Lambda Function, there's no need to use
this inside of your application code.
"""

import typing as T
import dataclasses

from .compat import need_cached_property
from .semantic_branch import (
    is_main_branch,
    is_develop_branch,
    is_feature_branch,
    is_build_branch,
    is_doc_branch,
    is_fix_branch,
    is_release_branch,
)
from .conventional_commits import (
    is_feat_commit,
    is_fix_commit,
    is_doc_commit,
    is_test_commit,
    is_utest_commit,
    is_itest_commit,
    is_ltest_commit,
    is_build_commit,
    is_publish_commit,
    is_release_commit,
)

if need_cached_property:  # pragma: no cover
    from cached_property import cached_property
else:  # pragma: no cover
    from functools import cached_property

try:
    from .cc_client import get_commit_message_and_committer
except ImportError:  # pragma: no cover
    pass
except:  # pragma: no cover
    raise


class CodeCommitEventTypeEnum:
    """
    Enumerate common CodeCommit notification event type.

    It is the value of the :meth:`CodeCommitEvent.event_type` method.
    """

    commit_to_branch = "commit_to_branch"
    commit_to_branch_from_merge = "commit_to_branch_from_merge"
    create_branch = "create_branch"
    delete_branch = "delete_branch"
    pr_created = "pr_created"
    pr_closed = "pr_closed"
    pr_updated = "pr_updated"
    pr_merged = "pr_merged"
    comment_on_pr_created = "comment_on_pr_created"
    comment_on_pr_updated = "comment_on_pr_updated"
    reply_to_comment = "reply_to_comment"
    approve_pr = "approve_pr"
    approve_rule_override = "approve_rule_override"
    unknown = "unknown"


@dataclasses.dataclass
class CodeCommitEvent:
    """
    Data container class to represent a CodeCommit notification event.
    """

    afterCommitId: str = dataclasses.field(default="")
    approvalStatus: str = dataclasses.field(default="")
    author: str = dataclasses.field(default="")
    beforeCommitId: str = dataclasses.field(default="")
    callerUserArn: str = dataclasses.field(default="")
    commentId: str = dataclasses.field(default="")
    commitId: str = dataclasses.field(default="")
    creationDate: str = dataclasses.field(default="")
    destinationCommit: str = dataclasses.field(default="")
    destinationCommitId: str = dataclasses.field(default="")
    destinationReference: str = dataclasses.field(default="")
    event: str = dataclasses.field(default="")
    isMerged: str = dataclasses.field(default="")
    inReplyTo: str = dataclasses.field(default="")
    lastModifiedDate: str = dataclasses.field(default="")
    mergeOption: str = dataclasses.field(default="")
    notificationBody: str = dataclasses.field(default="")
    oldCommitId: str = dataclasses.field(default="")
    overrideStatus: str = dataclasses.field(default="")
    pullRequestId: str = dataclasses.field(default="")
    pullRequestStatus: str = dataclasses.field(default="")
    referenceFullName: str = dataclasses.field(default="")
    referenceName: str = dataclasses.field(default="")
    referenceType: str = dataclasses.field(default="")
    repositoryId: str = dataclasses.field(default="")
    repositoryName: str = dataclasses.field(default="")
    revisionId: str = dataclasses.field(default="")
    sourceCommit: str = dataclasses.field(default="")
    sourceCommitId: str = dataclasses.field(default="")
    sourceReference: str = dataclasses.field(default="")
    title: str = dataclasses.field(default="")
    aws_account_id: str = dataclasses.field(default="")
    aws_region: str = dataclasses.field(default="")

    @classmethod
    def from_event(cls, event: dict) -> "CodeCommitEvent":
        kwargs = event["detail"].copy()
        if "repositoryNames" in kwargs:
            kwargs["repositoryName"] = kwargs.pop("repositoryNames")[0]
        repo_arn = event["resources"][0]
        parts = repo_arn.split(":")
        kwargs["aws_account_id"] = parts[4]
        kwargs["aws_region"] = parts[3]
        return cls(**kwargs)

    def to_env_var(self, prefix="") -> dict:
        return {(prefix + k).upper(): v for k, v in dataclasses.asdict(self).items()}

    @classmethod
    def from_env_var(cls, env_var: dict, prefix="") -> "CodeCommitEvent":
        field_set = {field.name for field in dataclasses.fields(cls)}
        kwargs = dict()
        for field_name in field_set:
            key = (prefix + field_name).upper()
            if key in env_var:
                kwargs[field_name] = env_var[key]
        return cls(**kwargs)

    @cached_property
    def event_type(self) -> str:
        if self.event == "referenceUpdated":
            if self.mergeOption:
                return CodeCommitEventTypeEnum.commit_to_branch_from_merge
            else:
                return CodeCommitEventTypeEnum.commit_to_branch
        elif self.event == "referenceCreated":
            return CodeCommitEventTypeEnum.create_branch
        elif self.event == "referenceDeleted":
            return CodeCommitEventTypeEnum.delete_branch
        elif self.event == "pullRequestCreated":
            if self.isMerged == "False" and self.pullRequestStatus == "Open":
                return CodeCommitEventTypeEnum.pr_created
            else:  # pragma: no cover
                return CodeCommitEventTypeEnum.unknown
        elif (
            self.event == "pullRequestStatusChanged"
            and self.pullRequestStatus == "Closed"
        ):
            return CodeCommitEventTypeEnum.pr_closed
        elif self.event == "pullRequestSourceBranchUpdated":
            return CodeCommitEventTypeEnum.pr_updated
        elif (
            self.event == "pullRequestMergeStatusUpdated"
            and self.isMerged == "True"
            and self.pullRequestStatus == "Closed"
        ):
            return CodeCommitEventTypeEnum.pr_merged
        elif self.event == "commentOnPullRequestCreated":
            if self.inReplyTo:
                return CodeCommitEventTypeEnum.reply_to_comment
            else:
                return CodeCommitEventTypeEnum.comment_on_pr_created
        elif self.event == "commentOnPullRequestUpdated":
            if self.inReplyTo:
                return CodeCommitEventTypeEnum.reply_to_comment
            else:
                return CodeCommitEventTypeEnum.comment_on_pr_updated
        elif (
            self.event == "pullRequestApprovalStateChanged"
            and self.approvalStatus == "APPROVE"
        ):
            return CodeCommitEventTypeEnum.approve_pr
        elif self.event == "pullRequestApprovalRuleOverridden":
            return CodeCommitEventTypeEnum.approve_rule_override
        else:  # pragma: no cover
            return CodeCommitEventTypeEnum.unknown

    @cached_property
    def event_description(self) -> str:  # pragma: no cover
        if self.is_commit_event:
            return (
                f"commit to {self.source_branch!r} branch, "
                f"commit id is {self.source_commit}, "
                f"commit message is {self.commit_message}."
            )
        elif self.is_pr_event:
            return (
                f"{self.event_type} "
                f"from {self.source_branch!r} branch to "
                f"{self.target_branch!r} branch, "
                f"commit id is {self.source_commit}, "
                f"commit message is {self.commit_message}."
            )
        elif self.is_comment_event:
            return (
                f"comment on pull request {self.pullRequestId!r} "
                f"comment id is {self.commentId!r}"
            )
        else:
            return ""

    # test Event Type
    @cached_property
    def is_commit_to_branch_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.commit_to_branch

    @cached_property
    def is_commit_to_branch_from_merge_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.commit_to_branch_from_merge

    @cached_property
    def is_commit_event(self) -> bool:
        return (
            self.is_commit_to_branch_event or self.is_commit_to_branch_from_merge_event
        )

    @cached_property
    def is_create_branch_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.create_branch

    @cached_property
    def is_delete_branch_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.delete_branch

    @cached_property
    def is_pr_created_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.pr_created

    @cached_property
    def is_pr_closed_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.pr_closed

    @cached_property
    def is_pr_update_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.pr_updated

    @cached_property
    def is_pr_merged_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.pr_merged

    @cached_property
    def is_comment_on_pr_created_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.comment_on_pr_created

    @cached_property
    def is_comment_on_pr_updated_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.comment_on_pr_updated

    @cached_property
    def is_reply_to_comment_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.reply_to_comment

    @cached_property
    def is_comment_event(self) -> bool:
        return self.is_comment_on_pr_created_event or self.is_reply_to_comment_event

    @cached_property
    def is_approve_pr_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.approve_pr

    @cached_property
    def is_approve_rule_override_event(self) -> bool:
        return self.event_type == CodeCommitEventTypeEnum.approve_rule_override

    @cached_property
    def is_pr_event(self) -> bool:
        return (
            self.is_pr_created_event
            or self.is_pr_update_event
            or self.is_pr_merged_event
            or self.is_pr_closed_event
        )

    @cached_property
    def is_pr_created_or_updated_event(self) -> bool:
        return self.is_pr_created_event or self.is_pr_update_event

    # additional property
    @cached_property
    def repo_name(self) -> str:
        return self.repositoryName

    @cached_property
    def source_branch(self) -> str:
        if self.is_pr_event:
            return self.sourceReference.replace("refs/heads/", "", 1)
        elif self.is_commit_event:
            return self.referenceName
        elif self.is_comment_event:  # pragma: no cover
            return ""
        elif self.is_approve_pr_event or self.is_approve_rule_override_event:
            return self.sourceReference.replace("refs/heads/", "", 1)
        else:  # pragma: no cover
            return ""

    @cached_property
    def source_commit(self) -> str:
        if self.is_pr_event:
            return self.sourceCommit
        elif self.is_commit_event:
            return self.commitId
        elif self.is_comment_event:
            return self.afterCommitId
        elif self.is_approve_pr_event or self.is_approve_rule_override_event:
            return self.sourceCommit
        else:  # pragma: no cover
            return ""

    @cached_property
    def target_branch(self) -> str:
        if self.is_pr_event:
            return self.destinationReference.replace("refs/heads/", "", 1)
        elif self.is_approve_pr_event or self.is_approve_rule_override_event:
            return self.destinationReference.replace("refs/heads/", "", 1)
        else:  # pragma: no cover
            return ""

    @cached_property
    def target_commit(self) -> str:
        if self.is_pr_event:
            return self.destinationCommit
        elif self.is_commit_event:
            return self.oldCommitId
        elif self.is_comment_event:
            return self.beforeCommitId
        elif self.is_approve_pr_event or self.is_approve_rule_override_event:
            return self.destinationCommit
        else:  # pragma: no cover
            return ""

    @cached_property
    def _source_commit_message_and_committer(
        self,
    ) -> T.Tuple[str, str]:  # pragma: no cover
        return get_commit_message_and_committer(
            repo_name=self.repo_name,
            commit_id=self.source_commit,
        )

    @cached_property
    def source_commit_message(self) -> str:  # pragma: no cover
        return self._source_commit_message_and_committer[0]

    @cached_property
    def commit_message(self) -> str:  # pragma: no cover
        return self.source_commit_message

    @cached_property
    def source_committer_name(self) -> str:  # pragma: no cover
        return self._source_commit_message_and_committer[1]

    @cached_property
    def committer_name(self) -> str:  # pragma: no cover
        return self.source_committer_name

    @cached_property
    def pr_id(self) -> str:
        return self.pullRequestId

    @cached_property
    def pr_status(self) -> str:
        return self.pullRequestStatus

    @cached_property
    def pr_is_open(self) -> bool:
        return self.pr_status == "Open"

    @cached_property
    def pr_is_merged(self) -> bool:
        return self.isMerged == "True"

    @cached_property
    def is_pr_from_develop_to_main(self) -> bool:
        return (
            self.is_pr_event
            and self.source_is_develop_branch
            and self.target_is_main_branch
        )

    @cached_property
    def is_pr_from_feature_to_main(self) -> bool:
        return (
            self.is_pr_event
            and self.source_is_feature_branch
            and self.target_is_main_branch
        )

    @cached_property
    def is_pr_from_hotfix_to_main(self) -> bool:
        return (
            self.is_pr_event
            and self.source_is_fix_branch
            and self.target_is_main_branch
        )

    # test branch name
    @cached_property
    def source_is_main_branch(self) -> bool:  # pragma: no cover
        return is_main_branch(self.source_branch)

    @cached_property
    def source_is_develop_branch(self) -> bool:  # pragma: no cover
        return is_develop_branch(self.source_branch)

    @cached_property
    def source_is_feature_branch(self) -> bool:  # pragma: no cover
        return is_feature_branch(self.source_branch)

    @cached_property
    def source_is_build_branch(self) -> bool:  # pragma: no cover
        return is_build_branch(self.source_branch)

    @cached_property
    def source_is_doc_branch(self) -> bool:  # pragma: no cover
        return is_doc_branch(self.source_branch)

    @cached_property
    def source_is_fix_branch(self) -> bool:  # pragma: no cover
        return is_fix_branch(self.source_branch)

    @cached_property
    def source_is_release_branch(self) -> bool:  # pragma: no cover
        return is_release_branch(self.source_branch)

    @cached_property
    def target_is_main_branch(self) -> bool:  # pragma: no cover
        return is_main_branch(self.target_branch)

    @cached_property
    def target_is_develop_branch(self) -> bool:  # pragma: no cover
        return is_develop_branch(self.target_branch)

    @cached_property
    def target_is_feature_branch(self) -> bool:  # pragma: no cover
        return is_feature_branch(self.target_branch)

    @cached_property
    def target_is_build_branch(self) -> bool:  # pragma: no cover
        return is_build_branch(self.target_branch)

    @cached_property
    def target_is_doc_branch(self) -> bool:  # pragma: no cover
        return is_doc_branch(self.target_branch)

    @cached_property
    def target_is_fix_branch(self) -> bool:  # pragma: no cover
        return is_fix_branch(self.target_branch)

    @cached_property
    def target_is_release_branch(self) -> bool:  # pragma: no cover
        return is_release_branch(self.target_branch)

    # test commit message
    @cached_property
    def is_feat_commit(self) -> bool:  # pragma: no cover
        return is_feat_commit(self.commit_message)

    @cached_property
    def is_fix_commit(self) -> bool:  # pragma: no cover
        return is_fix_commit(self.commit_message)

    @cached_property
    def is_doc_commit(self) -> bool:  # pragma: no cover
        return is_doc_commit(self.commit_message)

    @cached_property
    def is_test_commit(self) -> bool:  # pragma: no cover
        return is_test_commit(self.commit_message)

    @cached_property
    def is_utest_commit(self) -> bool:  # pragma: no cover
        return is_utest_commit(self.commit_message)

    @cached_property
    def is_itest_commit(self) -> bool:  # pragma: no cover
        return is_itest_commit(self.commit_message)

    @cached_property
    def is_ltest_commit(self) -> bool:  # pragma: no cover
        return is_ltest_commit(self.commit_message)

    @cached_property
    def is_build_commit(self) -> bool:  # pragma: no cover
        return is_build_commit(self.commit_message)

    @cached_property
    def is_publish_commit(self) -> bool:  # pragma: no cover
        return is_publish_commit(self.commit_message)

    @cached_property  # pragma: no cover
    def is_release_commit(self) -> bool:
        return is_release_commit(self.commit_message)
