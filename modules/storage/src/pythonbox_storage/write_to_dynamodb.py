import csv
import boto3
from botocore.exceptions import ClientError

BUCKET_NAME = "us-west-2-aws-staging"
BUCKET_REGION = "us-west-2"
INFECTIONS_DATA_FILE_KEY = "awsu-ilt/AWS-100-DEV/v2.2/binaries/input/lab-3-dynamoDB/InfectionsData.csv"
FILE_NAME = "InfectionsData.csv"
INFECTIONS_TABLE_NAME = "InfectionsLookup"
DELIMITER = ","

boto3.setup_default_session(profile_name="federated-federated")

def load_infections_data(
        tableName=INFECTIONS_TABLE_NAME,
        bucketRegion=BUCKET_REGION,
        bucket=BUCKET_NAME,
        fKey=INFECTIONS_DATA_FILE_KEY,
        FName=FILE_NAME):
    num_failures = 0
    try:
        # Create an S3 resource to download the infections data file from the
        # S3 bucket
#        S3 = boto3.resource('s3', bucketRegion)
#        try:
            # Check if you have permissions to access the bucket and then
            # retrieve a reference to it
#            S3.meta.client.head_bucket(Bucket=bucket)
#            myBucket = S3.Bucket(bucket)
#        except ClientError as err:
#            print("Could not find bucket")
#            print("Error message {0}".format(err))
#            num_failures = 9999
#            return num_failures
#        except Exception as err: 
#            print("Error message {0}".format(err))
#            num_failures = 9999
#            return num_failures

#        try:
            # Download the CSV-formatted infections data file
#            myBucket.download_file(fKey, FName)
#        except Exception as err:
#            print("Error message {0}".format(err))
#            print("Failed to download the infections data file from S3 bucket")
#            num_failures = 9999
#            return num_failures

        print("Reading infections data from file, going to begin upload")
        with open(FName, newline='') as fh:
            reader = csv.DictReader(fh, delimiter=DELIMITER)
            # Create a DynamoDB resource
            dynamodb = boto3.resource('dynamodb')

            # Retrieve a reference to the Infections table
            infections_table = dynamodb.Table(INFECTIONS_TABLE_NAME)

            # Add an item for each row in the file
            for row in reader:
                try:
                    add_item_to_table(
                        infections_table,
                        row['PatientId'],
                        row['City'],
                        row['Date'])
                except Exception as err:
                    print("Error message {0}".format(err))
                    num_failures += 1
            print("Upload completed.")
    except Exception as err:
        print("Failed to add item in {0}".format(tableName))
        print("Error message {0}".format(err))
        num_failures = 9999
    return num_failures


# Put an item in the infections table using the attribute values for
# PatientId, City, and Date attributes
def add_item_to_table(infections_table, patient_id, city, date):
    infections_table.put_item(
        Item={
            'PatientId': patient_id,
            'City': city,
            'Date': date})

if __name__ == '__main__':
    print("Going to load data")
    load_infections_data()

