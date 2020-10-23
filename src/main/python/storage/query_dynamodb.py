import boto3
from boto3.dynamodb.conditions import Key
import sys
from datetime import datetime, timedelta
import solution as dynamodb_solution

INFECTIONS_TABLE_NAME = "InfectionsLookup"
CITY_DATE_INDEX_NAME = "InfectionsByCityDate"

def query_by_city(city):
    print("City name is {0}".format(city))
    # Query Infections table based on the input city and count the number of
    # infections
    count_for_city = 0
    try:
        dynamodb = boto3.resource('dynamodb')

        recs = dynamodb.Table(INFECTIONS_TABLE_NAME).query(
            IndexName=CITY_DATE_INDEX_NAME,
            KeyConditionExpression=Key('City').eq(city)
        )

        # Retrieves and prints from recs dictionary returned by the query.
        for rec in recs['Items']:
            print("\t", rec['PatientId'], rec['Date'])
        count_for_city = len(recs['Items'])
        print("Count of Infections in the city: {0}".format(count_for_city))
    except Exception as err:
        print("Error Message: {0}".format(err))
    return count_for_city

# Query the table's global secondary index for items that contain the
# given city name
def query_city_related_items(dynamodb, infections_table_name, gsi_name, city):
    infections_table = dynamodb.Table(infections_table_name)
    recs = infections_table.query(
        IndexName=gsi_name,
        KeyConditionExpression=Key('City').eq(city)
    )
    
    return recs
    
if __name__ == '__main__': 
    print("Querying items by city") 
    query_by_city(city="Reno")
