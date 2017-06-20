import boto3
from botocore.exceptions import NoCredentialsError,ClientError
import sys

#  check that the ~/.aws/credentials file contains your credentials.
# [default]
# aws_access_key_id=AKIAJOYAKDDLE7WEQTQA
# aws_secret_access_key=6VTHrcErOfO50PqOOfBxHlGTeO5J0gzW3ySJ3U01

#profile = boto3.session.Session(profile_name='nordstrom-federated')
boto3.setup_default_session(profile_name="aws-federated")

def get_bucket_count():
    print("============================================");
    print("Welcome to the AWS Boto3 Storage SDK! Ready, Set, Go!");
    print("============================================");

    try:
        s3 = boto3.resource('s3')
        bucks = list(s3.buckets.all())
        no_of_buckets = len(list(s3.buckets.all()))
        print("You have", str(no_of_buckets), "Amazon Storage buckets.")
	for res in bucks:
	    print(res)
        return no_of_buckets

    except (NoCredentialsError, ClientError) as ex:
        print(ex)
        return 0


if __name__ == '__main__':
    get_bucket_count()
