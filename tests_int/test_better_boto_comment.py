# -*- coding: utf-8 -*-

from aws_codecommit.console import browse_code, browse_pr
from aws_codecommit.tests.boto_ses import bsm
from aws_codecommit.better_boto.pr import get_pull_request
from aws_codecommit.better_boto.comment import (
    PullRequestCommentThread,
)

from rich import print as rprint


class TestPullRequestCommentThread:
    def test(self):
        pr = get_pull_request(bsm, pr_id="12")
        console_url = browse_pr(
            aws_region=bsm.aws_region,
            repo_name=pr.targets[0].repo_name,
            pr_id=pr.pr_id,
        )
        print(f"preview PR at: {console_url}")

        console_url = browse_pr(
            aws_region=bsm.aws_region,
            repo_name=pr.targets[0].repo_name,
            pr_id=pr.pr_id,
            activity_tab=True,
        )
        print(f"preview PR comment at: {console_url}")
        with PullRequestCommentThread(bsm) as thread:
            thread.post_comment(
                pr_id=pr.pr_id,
                repo_name=pr.targets[0].repo_name,
                before_commit_id=pr.targets[0].src_commit,
                after_commit_id=pr.targets[0].dst_commit,
                content="hello 2",
            )
            thread.reply(content="reply 1")
            thread.reply(content="reply 2")



if __name__ == "__main__":
    from aws_codecommit.tests import run_cov_test

    run_cov_test(__file__, "aws_codecommit.better_boto.comment", preview=False)
