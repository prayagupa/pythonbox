from celery import Celery
import urllib
# pip3 install celery
# pip3 install celery[sqs]

AWS_ACCESS_KEY_ID='?'
AWS_SECRET_ACCESS_KEY='?'

broker_transport_options = {
    'predefined_queues': {
        'scheduling-queue': {
            'url': 'https://sqs.us-east-1.amazonaws.com/<<account_id>>/scheduling-queue',
            'access_key_id': AWS_ACCESS_KEY_ID,
            'secret_access_key': AWS_SECRET_ACCESS_KEY,
        }
    }
}

BROKER_URL = 'sqs://{0}:{1}@'.format(
    urllib.parse.quote(AWS_ACCESS_KEY_ID, safe=''),
    urllib.parse.quote(AWS_SECRET_ACCESS_KEY, safe='')
)

app = Celery('hello', 
        broker=BROKER_URL,
        broker_transport_options = broker_transport_options #{'queue_name_prefix': 'celery-'}
        )

@app.task
def hello():
    return 'hello luyanta'

