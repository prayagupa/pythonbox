import boto3
import time

from botocore.exceptions import NoCredentialsError, ClientError, EndpointConnectionError

INFECTIONS_TABLE_NAME = "InfectionsLookup"
HTTP_STATUS_SUCCESS = 200

LAB_S3_BUCKET_REGION = "us-west-2"
LAB_S3_INFECTIONS_DATA_FILE_KEY = "awsu-ilt/AWS-100-DEV/v2.2/binaries/input/lab-3-dynamoDB/InfectionsData.csv"
LAB_S3_PATIENT_REPORT_PREFIX = "awsu-ilt/AWS-100-DEV/v2.2/binaries/input/lab-3-dynamoDB/PatientRecord"
LAB_S3_FILE_KEY = "InfectionsData.csv"
LAB_S3_INFECTIONS_TABLE_NAME = "Infections"

def is_table_active(tableName=LAB_S3_INFECTIONS_TABLE_NAME):
    # Check if the given table exists and active
    try:
        resource = boto3.resource('dynamodb')
        table = resource.Table(tableName)
        if table.table_status == 'ACTIVE':
            return True
    except ClientError as err:
        if (err.response.get('Error').get('Code')
                == 'ResourceNotFoundException'):
            print("{0} Table not found".format(tableName))
    except Exception as err:
        print("Error message: {0}".format(err))
    return False

def remove_infections_table():
    # Name of the table
    table_name = INFECTIONS_TABLE_NAME

    # Removes the table_name from the region given as input
    rval = True
    if is_table_active(table_name):
        print("{0} Table exists and will be removed.".format(table_name))
        try:
            rval = False
            dynamoDB = boto3.resource('dynamodb')
            table = dynamoDB.Table(table_name)
            resp = table.delete()
            time.sleep(15)
            if resp['ResponseMetadata'][
                    'HTTPStatusCode'] == HTTP_STATUS_SUCCESS:
                rval = True
                print("{0} Table has been deleted.".format(table_name))
        except Exception as err:
            print(
                "Existing table deletion failed: {0} Table".format(table_name))
            print("Error Message: {0}".format(err))
            rval = False
    return rval


def create_infections_table_wrapper():
    # Name of the table
    table_name = INFECTIONS_TABLE_NAME

    # Attributes for partition keys and sort key
    patient_id_attr_name = 'PatientId'
    city_attr_name = 'City'
    date_attr_name = 'Date'

    # Name of the global secondary index
    gsi_name = 'InfectionsByCityDate'

    # Create a DynamoDB table and global secondary index
    create_infections_table(
        table_name,
        gsi_name,
        patient_id_attr_name,
        city_attr_name,
        date_attr_name)

def create_infections_table(
        table_name,
        gsi_name,
        patient_id,
        city_attr_name,
        date_attr_name):

    dynamodb = boto3.resource('dynamodb')
    try:
        # Create a table with:
        # - the given table name
        # - Patient ID as the partition key
        # - Patient ID, City, and Date attribute definitions
        # - provisioned throughput of 5 read capacity units and 10 write capacity units

        # - a global secondary index with
        # -- the given GSI name
        # -- City as partition key and Date as range key
        # -- all of the tables attributes projected into the index
        # -- provisioned throughput of 5 read capacity units and 5 write capacity units

        table = dynamodb.create_table(TableName=table_name,
                                      KeySchema=[{'AttributeName': patient_id, 'KeyType': 'HASH'}],
                                      AttributeDefinitions=[
                                          {'AttributeName': patient_id, 'AttributeType': 'S'},
                                          {'AttributeName': city_attr_name, 'AttributeType': 'S'},
                                          {'AttributeName': date_attr_name, 'AttributeType': 'S'}],
                                      ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10},
                                      GlobalSecondaryIndexes=[{'IndexName': gsi_name,
                                                               'KeySchema': [
                                                                   {'AttributeName': city_attr_name, 'KeyType': 'HASH'},

                                                                   {'AttributeName': date_attr_name,
                                                                    'KeyType': 'RANGE'}],

                                                               'Projection': {'ProjectionType': 'ALL'},
                                                               'ProvisionedThroughput': {'ReadCapacityUnits': 10,
                                                                                         'WriteCapacityUnits': 10}}],
                                      )
        # Wait for the table to become active
        time.sleep(5)
    except Exception as err:
        print("{0} Table could not be created".format(table_name))
        print("Error message {0}".format(err))

if __name__ == '__main__':
    print('===============================================================')
    print('Lab 3 DynamoDB - Infections Table creation')
    print('===============================================================')
    remove_infections_table()
    create_infections_table_wrapper()
    print(INFECTIONS_TABLE_NAME + " Table created")
