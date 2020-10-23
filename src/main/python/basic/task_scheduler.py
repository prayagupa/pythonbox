from datetime import datetime, timedelta
import time

while 1:
    print('Starting scheduler...')

    print (2 + 2)
    next_task_dt = datetime.now() + timedelta(hours=2)
    next_task_dt = next_task_dt.replace(minute=15)

    print('Scheduling next task at ' + str(next_task_dt))
    while datetime.now() < next_task_dt:
        time.sleep(1)


print ('Stopping scheduler')
