
import boto3
s3 = boto3.resource('s3')
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

today = datetime.today().strftime('%Y-%m-%d')
years_ago = datetime.now() - relativedelta(years=4)
three_years = years_ago.strftime('%Y-%m-%d')
three_years_ = years_ago.strftime('%Y/%m/%d')

bucket_name = 'lamatola--event-archive'
my_bucket = s3.Bucket(bucket_name)

def current_milli_time():
    return round(time.time() * 1000)

print("========")
print("" + three_years)
print("========")

start = current_milli_time()

## completed: 7646 ms
for file in my_bucket.objects.filter(Prefix=three_years_):

## completed: 12481 ms 
## for file in my_bucket.objects.all():
    obj = file.key
    if three_years in str(obj): 
        print("delete: " + obj)
        ## obj.delete()
#    else:
#        print("ignore: " + obj)

end = current_milli_time()

print("completed: " + str(end - start) + " ms")

