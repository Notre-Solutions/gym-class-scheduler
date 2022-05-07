from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()

import json
from datetime import datetime


weekday = {
  "Monday": 0,
  "Tuesday": 1,
  "Wednesday": 2,
  "Thursday": 3,
  "Friday": 4,
  "Saturday": 5,
  "Sunday": 6
}

def getClasses():
  with open('/Users/nyasha/development/sandbox/class_config.json', 'r') as f:
    classes = json.load(f)
  return classes

def bookClass(name,user,password,day, time):
  print(name,user,password)

def main():
  classes = getClasses() #Get users from table with todays resume_dttime
  keys = classes.keys()
  print(classes)
  for c in keys:
    name = classes[c]['Name']
    day = classes[c]['DayOfWeek']
    time = classes[c]['Time']
    user = classes[c]['Username']
    password = classes[c]['Password']
    tminus2 = weekday[day] - 2
    if tminus2 == -2:
      tminus2 = 5
    elif tminus2 == -1:
      tminus2 = 6
    today = datetime.today().weekday()

    if tminus2 == today:
      hr, minute = time.split(':')
      sched.add_job(
        lambda: bookClass(name,user,password, day, time), 
        trigger='cron',
        hour=hr,
        minute=minute
      )

@sched.scheduled_job('cron', hour=20, minute=16)
def scheduled_job():
    """
    """
    main()


if __name__ == "__main__":
  sched.start()
  sched.shutdown(wait=True)