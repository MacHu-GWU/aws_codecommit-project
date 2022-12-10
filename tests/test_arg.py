# -*- coding: utf-8 -*-

from aws_codecommit.better_boto.arg import NOTHING, resolve_kwargs


def test_resolve_kwargs():
    kwargs = resolve_kwargs(
        _mapper={"a": "A", "b": "B", "c": "C"},
        a=1,
        b="hello",
        c=NOTHING,
        d=[],
    )
    assert kwargs == {"A": 1, "B": "hello", "d": []}


if __name__ == "__main__":
    from aws_codecommit.tests import run_cov_test

    run_cov_test(__file__, "aws_codecommit.better_boto.arg", preview=False)
