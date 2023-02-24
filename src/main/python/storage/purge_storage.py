import boto3
from botocore.exceptions import ClientError

## aws_session = boto3.session.Session(profile_name='lamatolaprod')
## s3_client1 = aws_session.resource('s3')
s3_client = boto3.client('s3')

bucket_prefix="test-lamatola-log/"
filter_prefix="test-lamatola-log/"

try:
    policy_status = s3_client.put_bucket_lifecycle_configuration(
               Bucket='boto-lifecycle-test',
               LifecycleConfiguration={
                    'Rules': 
                           [
                             {
                             'Expiration':
                                {
                                 'Days': 1,
                                 'ExpiredObjectDeleteMarker': True
                                },
                             'Prefix': 'test-redshift-log/',
                             'Filter': {
                               'Prefix': 'test-redshift-log/',
                             },
                             'Status': 'Enabled',
                            }
                        ]})
except ClientError as e:
     print("Unable to apply bucket policy. \nReason:{0}".format(e))

