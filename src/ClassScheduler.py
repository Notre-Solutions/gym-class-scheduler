from apscheduler.schedulers.blocking import BlockingScheduler
import json
from datetime import datetime
from Utils import Utils, weekday
from logs import setup_logger
from BookClass import BookClass

sched = BlockingScheduler()
log = setup_logger(logger_name='Schedular')


def get_classes():
    class_config_file = Utils.get_config()['FILES']['CLASS_CONFIG']
    with open(class_config_file, 'r') as f:
        classes = json.load(f)
    return classes


def book_class(name, user, password, day, time):
    BookClass().book_class(user, password, name, time, day)


def main():
    classes = get_classes()  # Get users from table with todays resume_dttime
    keys = classes.keys()
    log.info(classes)
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
                lambda: book_class(name, user, password, day, time),
                trigger='cron',
                hour=hr,
                minute=minute
            )


@sched.scheduled_job('cron', hour=6)
def scheduled_job():
    """
    """
    main()


if __name__ == "__main__":
    log.info('Starting Schedular..')
    sched.start()
    sched.shutdown(wait=True)
