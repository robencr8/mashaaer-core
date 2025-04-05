from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def remind_user():
    logger.info("[Reminder] Daily user reminder triggered.")

scheduler = BackgroundScheduler()

scheduler.add_job(
    remind_user,
    'interval',
    hours=24,
    next_run_time=datetime.now() + timedelta(minutes=1),
    id='daily_reminder'
)

scheduler.start()

if __name__ == '__main__':
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down.")
