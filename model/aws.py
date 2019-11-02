#!`which python3`

import os
import boto3

class AWS:
    def __init__(self):
        self.session = boto3.Session(aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']) 
    
    def s3(self):
        return self.session.resource('s3')
