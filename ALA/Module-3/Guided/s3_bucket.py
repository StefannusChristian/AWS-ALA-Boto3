# Imports
import boto3
import os
from botocore.exceptions import ClientError

class AWS:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, aws_session_token: str, aws_secret_key: str):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        self.aws_secret_key = aws_secret_key
        self.s3_client = self.create_client()
        self.s3_resource = self.create_resource()

    def create_session(self):
        session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_key,
            aws_session_token=self.aws_session_token
        )
        return session

    def create_resource(self):
        s3_resource = boto3.resource('s3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                aws_session_token=self.aws_session_token
                )
        return s3_resource

    def create_client(self, region_name = None):
        if region_name is None:
            s3_client = boto3.client(
                's3',
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    aws_session_token=self.aws_session_token
                )
        else:
            s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    aws_session_token=self.aws_session_token,
                    region_name=region_name
                    )
        return s3_client

    def is_bucket_exist(self, bucket_name: str):
        bucket = self.s3_resource.Bucket(bucket_name)
        return True if bucket.creation_date else False

    def create_bucket(self, bucket_name: str, region=None):
        """Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param bucket_name: Bucket to create
        :param region: String region to create bucket in, e.g., 'us-west-2'
        :return: True if bucket created, else False
        """

        if self.is_bucket_exist(bucket_name):
            print(f'Bucket {bucket_name} already exists!')
            return

        # Create bucket
        try:
            if region is None: self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                location = {'LocationConstraint': region}
                self.s3_client.create_bucket(Bucket=bucket_name,
                                        CreateBucketConfiguration=location)
            print(f"Bucket {bucket_name} is successfully created!")

        except ClientError as e:
            print(e)
            return False
        return True

    def upload_file(self, file_name: str, bucket_name: str, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        s3_client = self.create_client()
        try:
            response = s3_client.upload_file(file_name, bucket_name, object_name)
            print(f"{file_name} successfully uploaded!")
        except ClientError as e:
            print(e)
            return False
        return True

    def static_website_hosting(self, bucket_name: str):
        s3_client = self.create_client()
        result = s3_client.get_bucket_website(Bucket=bucket_name)
        website_configuration = {
            'ErrorDocument': {'Key': './error.html'},
            'IndexDocument': {'Suffix': './index.html'},
        }
        s3_client.put_bucket_website(Bucket=bucket_name,
                      WebsiteConfiguration=website_configuration)

if __name__ == '__main__':
    ACCESS_ID = "ASIAUDVPQVMGSOWIVGYV"
    ACCESS_KEY = "tUyo0TgMo7Q26wf2Zw1QiFImJH1y5pgI/TM2scI1"
    SESSION_TOKEN = """
    FwoGZXIvYXdzEH4aDHPAkJknE2Th3ZUYMCLTAZRzCkbci+45beRXBoexM5cMoI9JNbtmjCiJ8uc6Z8L75WspFHoOkwkJAcOZKvi/DCipn+4LHdowTOBk8KZUYk7MlWNupLOhbn57LogUXWlSgpWh9N/OUsyIryyBEw2K+3VuxLpTfh+o7NZ5+KCdfWLKFjMgzlAXDSLlphuE9bbd/wZp37+A38UcsWYUPz3Ye0V2BVH9gy/mLcNDTH/bR9huG1aUh2IBWQYqnSFheNnnQKfVrALzjfSnUvw/ltfEExTJ30LPXvdhvVpiu6kW+pvTXwoo27CPqAYyLV8DmPIUyxNPL03no+AER/x4W1AzL0yxJ9jVXC0lx6tAsowAMcIh1c/idd8aEw==
    """
    SECRET_KEY = "DiRbwlz9El+scPQ0bwEElxwDNo+WcghXvL3Jmlma"

    aws = AWS(ACCESS_ID, ACCESS_KEY, SESSION_TOKEN, SECRET_KEY)
    bucket_name = "stefannus-bucket-138"
    session = aws.create_session()
    aws.create_bucket(bucket_name)
    aws.upload_file('./index.html',bucket_name)
    aws.upload_file('./error.html',bucket_name)
    aws.upload_file('./style.css',bucket_name)
    aws.upload_file('./script.js',bucket_name)
    aws.static_website_hosting(bucket_name)