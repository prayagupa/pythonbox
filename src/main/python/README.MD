
```
[ec2-user@ip-10-0-10-217 dynamoDBPythonLab]$ aws dynamodb list-tables
{
    "TableNames": [
        "InfectionsLookup" 
    ]
}
```

data-model

```
[ec2-user@ip-10-0-10-217 dynamoDBPythonLab]$ aws dynamodb describe-table --table-name InfectionsLookup
{
    "Table": {
        "TableArn": "arn:aws:dynamodb:us-west-2:129645770974:table/InfectionsLookup", 
        "AttributeDefinitions": [
            {
                "AttributeName": "City", 
                "AttributeType": "S"
            }, 
            {
                "AttributeName": "Date", 
                "AttributeType": "S"
            }, 
            {
                "AttributeName": "PatientId", 
                "AttributeType": "S"
            }
        ], 
        "GlobalSecondaryIndexes": [
            {
                "IndexSizeBytes": 0, 
                "IndexName": "InfectionsByCityDate", 
                "Projection": {
                    "ProjectionType": "ALL"
                }, 
                "ProvisionedThroughput": {
                    "NumberOfDecreasesToday": 0, 
                    "WriteCapacityUnits": 10, 
                    "ReadCapacityUnits": 10
                }, 
                "IndexStatus": "ACTIVE", 
                "KeySchema": [
                    {
                        "KeyType": "HASH", 
                        "AttributeName": "City"
                    }, 
                    {
                        "KeyType": "RANGE", 
                        "AttributeName": "Date"
                    }
                ], 
                "IndexArn": "arn:aws:dynamodb:us-west-2:129645770974:table/InfectionsLookup/index/InfectionsByCityDate", 
                "ItemCount": 0
            }
        ], 
        "ProvisionedThroughput": {
            "NumberOfDecreasesToday": 0, 
            "WriteCapacityUnits": 10, 
            "ReadCapacityUnits": 10
        }, 
        "TableSizeBytes": 0, 
        "TableName": "InfectionsLookup", 
        "TableStatus": "ACTIVE", 
        "KeySchema": [
            {
                "KeyType": "HASH", 
                "AttributeName": "PatientId"
            }
        ], 
        "ItemCount": 0, 
        "CreationDateTime": 1498069385.79
    }
}
```

Scan docs
--------

```
[ec2-user@ip-10-0-10-217 dynamoDBPythonLab]$ aws dynamodb scan  --table-name InfectionsLookup
{
    "Count": 0, 
    "Items": [], 
    "ScannedCount": 0, 
    "ConsumedCapacity": null
}
```
