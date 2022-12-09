# -*- coding: utf-8 -*-
# Copyright (c) 2022-2030, Sanhe Hu, husanhe@gmail.com
# License: all right reserved

"""
**What is this**

This is a lambda function that subscribe the SNS topic of the CodeCommit events
and trigger CodeBuild job accordingly.

You may have seen lots of CI system like CircleCI / GitHub Action. Usually
the CI service provider uses the YML file to identify when to trigger the
build job, and what environment variable will be passed to the build job.
In AWS CodeCommit + CodeBuild, there's no fancy equivalent syntax available in
``buildspec.yml`` file for trigger rule declaration. Instead, CodeCommit can
send rich information to AWS Lambda on almost all of CodeCommit events. It gives
the developer the flexibility to implement arbitrary trigger rules and can do
far more fancy things comparing to other CI service providers.

**Prerequisite**

**Trigger Rule**

By default, it will trigger build job if:

1. Commit pushed to master branch.
2. Create A PR.
3. Commit pushed to a PR.
4. Merge PR.

**How to deploy this**

You can create an AWS Lambda Function with Python3.7+ runtime, and just
copy and paste into the code editor manually.

Configurations:

- Runtime: Python3.7+
- Timeout: 10 sec timeout (usually it takes 3 sec)
- Memory: 128 MB
- IAM: need these AWS Managed policies:
    - AWSLambdaBasicExecutionRole: for lambda execution
    - AmazonSNSReadOnlyAccess: read CodeCommit event from SNS
    - AWSCodeBuildDeveloperAccess: to trigger the build job
    - AWSCodeCommitPowerUser: to put automate comment and add commit to repo
    - AmazonS3FullAccess: store event history in specific S3 location,
        full access to specific S3 folder is fine.
- Add Trigger: choose "SNS", choose the SNS topic that receives event from
    CodeCommit notification or CodeBuild notification.

**NOTE**

Even you can see lots of other AWS Chalice related files,
this Lambda should be manually deployed in the console.

**Configure SNS**

1. Goto AWS SNS Console https://us-east-1.console.aws.amazon.com/sns/v3/home?region=us-east-1#/topics
    click "Create Topic"
2. Set
    - Type: "Standard"
    - Name: just give it a name, I use "cicd"
    - Access Policy: click advance and paste the following JSON::

        {
            "Version": "2008-10-17",
            "Id": "__default_policy_ID",
            "Statement": [
                {
                    "Sid": "__default_statement_ID",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "codestar-notifications.amazonaws.com"
                    },
                    "Action": "SNS:Publish",
                    "Resource": "arn:aws:sns:{your_aws_region}:{your_aws_account_id}:{your_sns_topic_name}"
                }
            ]
        }
    - Leave other option as default

**Configure CodeBuild**

We would like to let CodeBuild to send events to SNS topic, so we can
react accordingly.

1. Go to your CodeBuild project, click on "Notify" -> "Create notification rule"
2. Give it a name, I recommend to use your CodeBuild project name as prefix,
    like this "{codebuild_project_name}-all-event"
3. Detail type: Full -> Select All
4. Targets: choose the SNS topic you just created.

**Configure CodeCommit**

We would like to let CodeCommit event to send events to SNS topic, so we can
react accordingly.

1. Go to your CodeCommit repository, click on "Notify" -> "Create notification rule"
2. Give it a name, I recommend to use your CodeCommit repository name as prefix,
    like this "{codecommit_repository_name}-all-event"
3. Detail type: Full -> Select All
4. Targets: choose the SNS topic you just created.
"""

from typing import Optional, List
import json
import logging
import dataclasses
from datetime import datetime

import boto3
from aws_codecommit.notification import (
    CodeCommitEvent,
    is_certain_semantic_branch,
)
from aws_codecommit.cc_client import (
    get_text_file_content,
    post_comment_for_pull_request,
    reply_comment,
    update_comment,
)
from aws_codebuild.notification import CodeBuildEvent

boto_ses = boto3.session.Session()

cc_client = boto_ses.client("codecommit")
cb_client = boto_ses.client("codebuild")
s3_client = boto_ses.client("s3")

S3_BUCKET = "501105007192-us-east-1-data"
S3_PREFIX = "cicd_events"

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def header1(msg: str):
    logger.info("{:=^80}".format(f" {msg} "))


def header2(msg: str):
    logger.info("{:-^80}".format(f" {msg} "))


class CommitMessagePatternEnum:
    no_ci = "no ci"


class EventSourceEnum:
    codecommit = "codecommit"
    codebuild = "codebuild"


def identify_event_source(event: dict) -> str:
    """
    Identify that whether the event is from CodeCommit or CodeBuild.
    """
    if event["source"] == "aws.codecommit":
        return EventSourceEnum.codecommit
    elif event["source"] == "aws.codebuild":
        return EventSourceEnum.codebuild
    else:  # pragma: no cover
        raise NotImplementedError


# Parse codebuild-projects.json
class BuildJob:
    """
    Thin abstraction of a CodeBuild build job run. One BuildJob = trigger build job
    once.

    :param start_build_method: the codebuild boto3 client method name, could be
        None, "start_build", "start_build_batch"
    :param start_build_kwargs: the keyword argument that passed into the method
    """

    def __init__(
        self,
        start_build_method: Optional[str],
        start_build_kwargs: dict,
    ):
        self.start_build_method: str = start_build_method
        self.start_build_kwargs: dict = start_build_kwargs
        self.env_var = {}
        self.build_project: str = ""
        self.aws_account_id: str = ""
        self.aws_region: str = ""
        self.repo_name: str = ""
        self.is_pr: bool = False
        self.pr_id: str = ""
        self.before_commit_id: str = ""
        self.after_commit_id: str = ""
        self.commit_message: str = ""
        self.build_run_id: str = ""

    @property
    def build_run_console_url(self) -> str:
        return (
            f"https://{self.aws_region}.console.aws.amazon.com/"
            f"codesuite/codebuild/{self.aws_account_id}/"
            f"projects/{self.build_project}/"
            f"build/{self.build_run_id}/?region={self.aws_region}"
        )

    def upsert_env_var(self, key: str, value: str):
        """
        Update environment variable information for the build job metadata.
        """
        is_update = False
        for dct in self.start_build_kwargs.get(
            "environmentVariablesOverride", []
        ):
            if dct["name"] == key:
                dct["value"] = value
                is_update = True
        if is_update is False:
            self.start_build_kwargs.get(
                "environmentVariablesOverride", []
            ).append(
                dict(name=key, value=value, type="PLAINTEXT")
            )
        self.env_var[key] = value

    def start_build(self) -> str:
        """
        Invoke ``codebuild_clint.start_build`` or ``start_build_batch`` API.

        :return: the build run id
        """
        res = getattr(cb_client, self.start_build_method)(**self.start_build_kwargs)
        if "buildBatch" in res:
            self.build_run_id = res["buildBatch"]["id"]
        elif "build" in res:
            self.build_run_id = res["build"]["id"]
        else:  # pragma: no cover
            raise NotImplementedError
        logger.info(f"  preview build job run at: {self.build_run_console_url}")
        return self.build_run_id


@dataclasses.dataclass
class CodeBuildProjectConfig:
    project_name: str = ""
    is_batch_job: bool = False
    buildspec: str = ""


def parse_codebuild_projects_config(
    repo_name: str,
    commit_id: str,
    codebuild_projects_json_path: str = "codebuild-projects.json",
) -> List[CodeBuildProjectConfig]:
    """
    Each git repo that use codebuild should have a ``codebuild-projects.json``
    in the repo. It overrides some Codebuild configurations, and guide
    the lambda how to trigger the build job.

    The data structure is like below, each json object represent a definition
    of a build job::

        [
            {
                "project_name": "aws_data_lab_web_app-project",
                "is_batch_job": true,
                "buildspec": "path-to-buildspec.yml", (optional field)
            },
            {
                ...
            }
            ...
        ]

    It defines how this project should be built. You could use one or many
    codebuild project to build the same repo in different way.

    :param repo_name: the CodeCommit repo name
    :param commit_id: the commit id you want to trigger build job from
    :param codebuild_projects_json_path: json file location
    """
    content = get_text_file_content(
        repo_name=repo_name,
        commit_id=commit_id,
        file_path=codebuild_projects_json_path,
    )
    cb_project_config_list = [
        CodeBuildProjectConfig(**dct)
        for dct in json.loads(content)
    ]
    return cb_project_config_list


def to_env_var_override(env_var: dict) -> List[dict]:
    return [
        dict(name=key, value=value, type="PLAINTEXT")
        for key, value in env_var.items()
    ]


def extract_build_job_from_codecommit_event(
    cc_event: CodeCommitEvent,
) -> List[BuildJob]:
    """
    Implement the logic that when we trigger a codebuild job based on
    what Git event.
    """
    cb_project_config_list = parse_codebuild_projects_config(
        repo_name=cc_event.repo_name,
        commit_id=cc_event.source_commit,
    )

    jobs = list()

    # initialize job based on CodeBuild project config
    for cb_project_config in cb_project_config_list:
        if cb_project_config.is_batch_job:
            start_build_method = "start_build_batch"
        else:
            start_build_method = "start_build"
        start_build_kwargs = dict(projectName=cb_project_config.project_name)
        if cb_project_config.buildspec:
            start_build_kwargs["buildspecOverride"] = cb_project_config.buildspec
        job = BuildJob(
            start_build_method=start_build_method,
            start_build_kwargs=start_build_kwargs,
        )
        job.build_project = cb_project_config.project_name
        jobs.append(job)

    for job in jobs:
        job.start_build_kwargs["sourceVersion"] = cc_event.source_commit

        # add CodeCommit event data to CodeBuild job environment variable
        env_var = cc_event.to_env_var(prefix="CC_EVENT_")
        job.start_build_kwargs["environmentVariablesOverride"] = (
            to_env_var_override(env_var)
        )
        job.env_var = env_var
        job.aws_account_id = cc_event.aws_account_id
        job.aws_region = cc_event.aws_region
        job.repo_name = cc_event.repo_name
        job.is_pr = cc_event.is_pr_event
        job.pr_id = cc_event.pr_id
        job.before_commit_id = cc_event.source_commit
        job.after_commit_id = cc_event.target_commit

    return jobs


def is_layer_branch(name: str) -> bool:
    return is_certain_semantic_branch(name, ["layer", ])


def do_we_trigger_build_job(cc_event: CodeCommitEvent) -> bool:
    """
    This function defines whether we should trigger an AWS CodeBuild build job.
    This solution designed for any type of project for any programming language
    and for any Git Workflow. This function allow you to customize your own
    git branching rule and git commit rule, decide when to trigger the build.
    """
    # won't trigger build direct commit
    if cc_event.is_commit_event:
        logger.info(
            f"we don't trigger build job for "
            f"event type {cc_event.event_type!r} on {cc_event.source_branch}"
        )
        return False
    # run build job if it is a Pull Request related event
    elif (
        cc_event.is_pr_created_event
        or cc_event.is_pr_update_event
    ):
        # we don't trigger if commit message has 'NO BUILD'
        if cc_event.commit_message.startswith(CommitMessagePatternEnum.no_ci):
            logger.info(
                f"we DO NOT trigger build job for "
                f"commit message {cc_event.commit_message!r}"
            )
            return False

        # we don't trigger if source branch is not valid branch
        if not (
            cc_event.source_is_feature_branch
            or is_layer_branch(cc_event.source_branch)
            or cc_event.source_is_release_branch
            or cc_event.source_is_hotfix_branch
        ):
            logger.info(
                "we DO NOT trigger build job "
                f"if PR source branch is {cc_event.target_branch!r}"
            )
            return False

        # we don't trigger if target branch is not main
        if not cc_event.target_is_main_branch:
            logger.info(
                "we DO NOT trigger build job "
                "if PR target branch is not 'main' "
                f"it is {cc_event.target_branch!r}"
            )
            return False

        if (
            # on feature branch, but has invalid commit message
            (
                cc_event.is_pr_created_or_updated_event
                and cc_event.is_feature_branch
                and (
                    not (  # list of valid commit here
                        cc_event.is_feat_commit
                        or cc_event.is_build_commit
                        or cc_event.is_pub_commit
                        or cc_event.is_utest_commit
                        or cc_event.is_itest_commit
                        or cc_event.is_ltest_commit
                    )
                )
            )
            or
            # on layer branch, but has invalid commit message
            (
                cc_event.is_pr_created_or_updated_event
                and is_layer_branch(cc_event.source_branch)
                and (
                    not (  # list of valid commit here
                        cc_event.is_feat_commit
                        or cc_event.is_build_commit
                        or cc_event.is_pub_commit
                        or cc_event.is_utest_commit
                    )
                )
            )
            or
            # on release branch, but has invalid commit message
            (
                cc_event.is_pr_created_or_updated_event
                and cc_event.is_release_branch
                and (
                    not (  # list of valid commit here
                        cc_event.is_test_commit
                        or cc_event.is_fix_commit
                        or cc_event.is_rls_commit
                    )
                )
            )
            or
            # on hotfix branch, but has invalid commit message
            (
                cc_event.is_pr_created_or_updated_event
                and cc_event.is_hotfix_branch
                and (
                    not (  # list of valid commit here
                        cc_event.is_fix_commit
                    )
                )
            )
        ):
            logger.info(
                "we DO NOT trigger build job "
                f"for commit message {cc_event.commit_message!r} "
                f"on {cc_event.source_branch!r} branch"
            )
            return False
        return True
    # always trigger on PR merge event
    elif cc_event.is_pr_merged_event:
        return True
    # we don't trigger on other event
    elif (
        cc_event.is_create_branch_event
        or cc_event.is_delete_branch_event
        or cc_event.is_comment_event
        or cc_event.is_approve_pr_event
    ):
        return False
    else:
        return False


CI_DATA_PREFIX = "CI_DATA_"


@dataclasses.dataclass
class CIData:
    """
    CI related data, will be available in environment variable.
    """
    commit_message: str = ""
    comment_id: str = ""

    def add_to_job_env_var(
        self,
        job: BuildJob,
        prefix: "",
    ):
        for attr, value in dataclasses.asdict(self).items():
            key = (prefix + attr).upper()
            job.upsert_env_var(key, value)

    @classmethod
    def from_env_var(
        cls,
        env_var: dict,
        prefix="",
    ) -> 'CIData':
        field_set = {field.name for field in dataclasses.fields(cls)}
        kwargs = dict()
        for field_name in field_set:
            key = (prefix + field_name).upper()
            if key in env_var:
                kwargs[field_name] = env_var[key]
        return cls(**kwargs)


def handle_codecommit_event(cc_event: CodeCommitEvent):
    """
    What to do about codecommit event

    :param cc_event:
    :return:
    """
    header2("handle CodeCommit event ...")

    logger.info(
        f"detected event type = {cc_event.event_type}, "
        f"event description = {cc_event.event_description}"
    )

    # identify if we trigger the job
    if do_we_trigger_build_job(cc_event) is not True:
        return

    # analyze event
    jobs = extract_build_job_from_codecommit_event(cc_event)

    for job in jobs:
        logger.info(
            f"run ``codebuild_client.{job.start_build_method}(projectName={job.build_project!r})`` ..."
        )
        ci_data = CIData()
        # create a comment thread to the PR for this build job
        if job.is_pr:
            # update conditional attributes value
            job.commit_message = cc_event.commit_message

            pr_commit_console_url = (
                f"https://{job.aws_region}.console.aws.amazon.com/"
                f"codesuite/codecommit/repositories/{job.repo_name}/"
                f"pull-requests/{job.pr_id}/"
                f"commit/{job.before_commit_id}?region={job.aws_region}"
            )
            build_job_comment_id = post_comment_for_pull_request(
                repo_name=job.repo_name,
                pr_id=job.pr_id,
                before_commit_id=job.before_commit_id,
                after_commit_id=job.after_commit_id,
                content="\n".join([
                    "## 🌴 A build run is triggered, let's relax.",
                    "",
                    f"- commit id: [{job.before_commit_id[:7]}]({pr_commit_console_url})",
                    f"- commit message: \"{cc_event.commit_message.strip()}\"",
                    f"- committer name: \"{cc_event.committer_name.strip()}\"",
                ]),
            )

            ci_data.comment_id = build_job_comment_id
            ci_data.commit_message = cc_event.commit_message

            # pass in the comment id into the build job env var,
            # so we can reply to the thread during the build job run
            ci_data.add_to_job_env_var(job, prefix=CI_DATA_PREFIX)

            build_run_id = job.start_build()

            # update the comment content, include the build job link
            update_comment(
                comment_id=build_job_comment_id,
                content="\n".join([
                    "## 🌴 A build run is triggered, let's relax.",
                    "",
                    f"- build run id: [{build_run_id}]({job.build_run_console_url})",
                    f"- commit id: [{job.after_commit_id[:7]}]({pr_commit_console_url})",
                    f"- commit message: \"{cc_event.commit_message.strip()}\"",
                    f"- committer name: \"{cc_event.committer_name.strip()}\"",
                ]),
            )

        else:
            build_run_id = job.start_build()


def handle_codebuild_event(cb_event: CodeBuildEvent):
    """
    What to do about codebuild event?

    1. When a code build run is started or the status is changed, we want to
        automatically put a comment to the CodeCommit activity in PR.
        We need to know the ``comment_id`` explicitly. This ``comment_id``
        is provided by the previous lambda function invoke that actually did the
        ``start_build`` API call.
    """
    logger.info("handle CodeBuild event ...")

    # analyze event
    if (
        cb_event.is_state_in_progress
        or cb_event.is_state_failed
        or cb_event.is_state_succeeded
    ):
        logger.info(f"handle build status change event {cb_event.build_status!r}...")
        res = cb_client.batch_get_builds(ids=[cb_event.buildUUID, ])
        env_var = {
            dct["name"]: dct["value"]
            for dct in res["builds"][0]["environment"]["environmentVariables"]
        }
        comment_id = env_var[f"{CI_DATA_PREFIX}COMMENT_ID"]
        if cb_event.build_status == "SUCCEEDED":
            comment = "🟢 Build Run SUCCEEDED"
        elif cb_event.build_status == "FAILED":
            comment = "🔴 Build Run FAILED"
        elif cb_event.build_status == "STOPPED":
            comment = "⚫ Build Run STOPPED"
        else:
            raise NotImplementedError
        reply_comment(comment_id=comment_id, content=comment)


def encode_partition_key(dt: datetime) -> str:
    """
    Figure out the s3 partition part based on the given datetime.
    """
    return "/".join([
        f"year={dt.year}/"
        f"month={str(dt.month).zfill(2)}/"
        f"day={str(dt.day).zfill(2)}/"
    ])


def lambda_handler(event: dict, context):
    """
    """
    header1("START")
    header2("received SNS event:")
    ci_event = json.loads(event["Records"][0]["Sns"]["Message"])
    event["Records"][0]["Sns"]["Message"] = ci_event
    logger.info(json.dumps(event, indent=4))
    event_source = identify_event_source(ci_event)

    if event_source == EventSourceEnum.codecommit:
        cc_event = CodeCommitEvent.from_event(ci_event)
        header2("dump CodeCommit event to s3 ...")
        utc_now = datetime.utcnow()
        time_str = utc_now.strftime("%Y-%m-%dT%H-%M-%S.%f")
        s3_key = (
            f"{S3_PREFIX}/codecommit/{cc_event.repo_name}/"
            f"{encode_partition_key(utc_now)}/"
            f"{time_str}_{cc_event.repo_name}.json"
        )
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(event, indent=4),
        )
        # This aws console link to show codecommit event json file content
        s3_console_url = (
            f"https://{cc_event.aws_region}.console.aws.amazon.com/"
            f"s3/buckets/{S3_BUCKET}/object/"
            f"select?region={cc_event.aws_region}&prefix={s3_key}"
        )
        logger.info(f"preview event at: {s3_console_url}")
        handle_codecommit_event(cc_event)
    elif event_source == EventSourceEnum.codebuild:
        cb_event = CodeBuildEvent.from_event(ci_event)
        header2("dump CodeBuild event to s3 ...")
        utc_now = datetime.utcnow()
        time_str = utc_now.strftime("%Y-%m-%dT%H-%M-%S.%f")
        s3_key = (
            f"{S3_PREFIX}/codebuild/{cb_event.buildProject}/"
            f"{encode_partition_key(utc_now)}/"
            f"{time_str}_{cb_event.buildId}.json"
        )
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(ci_event, indent=4),
        )
        # This aws console link to show codebuild event json file content
        s3_console_url = (
            f"https://{cb_event.awsRegion}.console.aws.amazon.com/"
            f"s3/object/"
            f"{S3_BUCKET}?region={cb_event.awsRegion}&prefix={s3_key}"
        )
        logger.info(f"  preview event at: {s3_console_url}")
        handle_codebuild_event(cb_event)
    else:
        raise NotImplementedError
