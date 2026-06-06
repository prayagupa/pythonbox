from celery import Celery
import urllib

# pip3 install celery
# pip3 install celery[sqs]
# celery -A celery_example worker --loglevel=DEBUG

AWS_ACCESS_KEY_ID = '?'
AWS_SECRET_ACCESS_KEY = '?'

broker_transport_options = {
    'predefined_queues': {
        'my-queue': {
            'url': 'https://sqs.us-east-1.amazonaws.com/<<ACC_ID>>/my-queue',
            'access_key_id': AWS_ACCESS_KEY_ID,
            'secret_access_key': AWS_SECRET_ACCESS_KEY,
        }
    }
}

BROKER_URL = 'sqs://{0}:{1}@'.format(
    urllib.parse.quote(AWS_ACCESS_KEY_ID, safe=''),
    urllib.parse.quote(AWS_SECRET_ACCESS_KEY, safe='')
)

rabbit_mq_broker = 'amqps://username:pass@my.mq.us-east-1.amazonaws.com:5671'

app = Celery('hello',
             broker=rabbit_mq_broker
             )


@app.task
def hello():
    return 'hello luyanta'
