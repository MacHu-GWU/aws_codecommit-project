# -*- coding: utf-8 -*-

import boto3

boto_ses = boto3.session.Session()

cc_client = boto_ses.client("codecommit")
