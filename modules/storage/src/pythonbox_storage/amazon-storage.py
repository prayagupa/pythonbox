import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import sys
import logging
from datetime import datetime, timedelta

#  check that the ~/.aws/credentials file contains your credentials.
# [aws-federated]
# aws_access_key_id=AKIAJOYAKDDLE7WEQTQA
# aws_secret_access_key=6VTHrcErOfO50PqOOfBxHlGTeO5J0gzW3ySJ3U01

boto3.setup_default_session(profile_name="lamatola-dev")


# boto3.setup_default_session(region_name='us-west-2')

def get_bucket_count():
    print("============================================");
    print("Welcome to the AWS Boto3 Storage SDK! Ready, Set, Go!");
    print("============================================");

    try:
        s3 = boto3.resource('s3')
        bucks = list(s3.buckets.all())
        no_of_buckets = len(list(s3.buckets.all()))
        print("[INFO] You have", str(no_of_buckets), "Amazon Storage buckets.")
        for res in bucks:
            print(res)
        return no_of_buckets

    except (NoCredentialsError, ClientError) as ex:
        print(ex)
        return 0


def upload_file(bucket_name, file_name, object_name):
    s3_client = boto3.client('s3')
    print("uploading " + file_name + " to storage " + object_name)

    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
        print("success: " + str(response))
    except ClientError as e:
        logging.error(e)
        print(e)
        return False
    return True


def read_all(bucket_name):
    s3 = boto3.resource('s3')
    print("-- read all buckets --")
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.all():
        key = obj.key
        body = obj.get()['Body'].read()

def read_by_prefix(bucket_name, b_prefix):
    print("-- read by prefix --")
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    objects = bucket.objects.filter(Prefix=b_prefix)
    
    for obj in objects:
        print(obj)
        print("")

def delete_by_prefix(bucket_name, b_prefix):
    print("-- delete by prefix --")
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    objects = bucket.objects.filter(Prefix=b_prefix)
    
    for obj in objects:
        print(obj)
        print("")

def read_object_by_path(bucket_name, object_name):
    s3 = boto3.resource('s3')
    print("-- read by path --")
    object = s3.Object(bucket_name, object_name)
    data = object.get()['Body'].read()
    print(str(data))


if __name__ == '__main__':
    get_bucket_count()

    source_file_name = 'source.csv'
    bucket_name = 'lamatola-bucket-dev'
    bucket_name2 = 'dev-event-archive'

    prefix_1='2022-10-22'
    prefix_2='2017/'
    object_name = '2022-10-22/' + source_file_name
    object_name_2 = '2017-01-02/2017-01-02_394364409_436980216_1_1.csv'

    ## upload_file(bucket_name, source_file_name, object_name)
    
    read_object_by_path(bucket_name2, object_name_2)

    read_by_prefix(bucket_name2, prefix_2)
