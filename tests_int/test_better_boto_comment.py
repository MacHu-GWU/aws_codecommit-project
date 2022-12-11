# -*- coding: utf-8 -*-

from aws_codecommit.console import browse_code, browse_pr, browse_commit
from aws_codecommit.tests.boto_ses import bsm

from aws_codecommit.better_boto.pr import get_pull_request
from aws_codecommit.better_boto.comment import (
    CommentThread,
)
from aws_codecommit.better_boto.commit import (
    get_commit,
    get_branch_last_commit_id,
)
from aws_codecommit.better_boto.create_commit import (
    create_commit,
    put_file,
)
from aws_codecommit.better_boto.file import get_file

from rich import print as rprint


class TestPullRequestCommentThread:
    def test(self):
        """
        In order to test this, create a PR, and copy the PR id to here.
        """
        PR_ID = "12"
        pr = get_pull_request(bsm, pr_id=PR_ID)
        # rprint(pr)
        target = pr.targets[0]
        repo_name = target.repo_name
        pr_id = pr.pr_id
        print("")
        print(f"Pull request {target.src_ref!r} -> {target.dst_ref}")

        console_url = browse_pr(
            aws_region=bsm.aws_region,
            repo_name=repo_name,
            pr_id=pr_id,
        )
        print(f"preview PR at: {console_url}")

        # --- PR comment thread
        # console_url = browse_pr(
        #     aws_region=bsm.aws_region,
        #     repo_name=repo_name,
        #     pr_id=pr_id,
        #     activity_tab=True,
        # )
        # print(f"preview PR comment at: {console_url}")
        # with CommentThread(bsm) as thread:
        #     thread.post_comment(
        #         pr_id=pr.pr_id,
        #         repo_name=repo_name,
        #         before_commit_id=target.dst_commit,
        #         after_commit_id=target.src_commit,
        #         content=f"this is a PR from {target.src_ref!r} -> {target.dst_ref}",
        #     )
        #     thread.reply(content=f"source commit: {target.src_commit}")
        #     thread.reply(content=f"destination commit: {target.dst_commit}")

        # --- commit comment thread
        console_url = browse_commit(
            aws_region=bsm.aws_region,
            repo_name=target.repo_name,
            commit_id=target.src_commit,
        )
        print(f"preview commit comment at: {console_url}")

        parent_commit_id = get_commit(
            bsm,
            repo_name=repo_name,
            commit_id=target.src_commit,
        ).parent_commit_ids[0]

        with CommentThread(bsm) as thread:
            thread.post_comment(
                repo_name=pr.targets[0].repo_name,
                before_commit_id=parent_commit_id,
                after_commit_id=target.src_commit,
                content=f"parent = {parent_commit_id}, commit = {target.src_commit}",
            )
            thread.reply(content=f"parent = {parent_commit_id}")
            thread.reply(content=f"target = {target.src_commit}")

        # --- create commit
        # last_commit_id = get_branch_last_commit_id(
        #     bsm,
        #     repo_name=target.repo_name,
        #     branch_name=target.src_ref.split("/")[-1],
        # )
        # print(target.dst_commit)
        # print(last_commit_id)

        # print(target.src_ref)
        # print(target.src_commit)
        # commit = create_commit(
        #     bsm=bsm,
        #     repo_name=target.repo_name,
        #     branch_name=target.src_ref.split("/")[-1],
        #     parent_commit_id=target.src_commit,
        #     author_name="alice",
        #     author_email="alice@example.com",
        #     commit_message="overwrite",
        #     put_files=[
        #         dict(
        #             filePath="chore.txt",
        #             fileMode="NORMAL",
        #             fileContent="god",
        #         )
        #     ]
        # )
        # rprint(commit)

        # commit = put_file(
        #     bsm=bsm,
        #     repo_name=pr.targets[0].repo_name,
        #     branch_name=pr.targets[0].src_ref.split("/")[-1],
        #     parent_commit_id=pr.targets[0].dst_commit,
        #     file_path="chore.txt",
        #     file_content="a\nb\nc\nd",
        #     # file_content="a\nx\ny\nd",
        #     author_name="alice",
        #     author_email="alice@example.com",
        #     commit_message="b",
        # )
        # rprint(commit)
        # if commit:
        #     print(f"preview commit details at: {commit.browse_console_url}")
        #
        # file = get_file(
        #     bsm,
        #     repo_name=pr.targets[0].repo_name,
        #     file_path="chore.txt",
        #     commit_id=last_commit_id,
        # )
        # print(file.get_text())


if __name__ == "__main__":
    from aws_codecommit.tests import run_cov_test

    run_cov_test(__file__, "aws_codecommit.better_boto.comment", preview=False)
