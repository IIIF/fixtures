#!`which python3`

import os
import boto3

class AWS:
    def __init__(self):
        if 'AWS_ACCESS_KEY_ID' in os.environ and 'AWS_SECRET_ACCESS_KEY' in os.environ:
            self.session = boto3.Session(aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']) 
        else:
            self.session = boto3.Session() 
    
    def s3(self):
        return self.session.resource('s3')

    def client(self, service, region='us-east-1'):
        return self.session.client(service, region_name=region)
