import logging, os
import pandas as pd
from .models import HistoricalData, RecentData
from django_apscheduler.models import DjangoJob
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job, register_events
from .DataCollector import collectHistoryData, collectRecentData, collectTrainingData
from .importers import replace_historical_data_from_csv
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger('scheduler')

# init scheduler
scheduler = BackgroundScheduler()
# add DjangoJobStore to the scheduler
scheduler.add_jobstore(DjangoJobStore(), "default")

# reset the autoincrement id of table
def reset_autoincrement(model):
    """Reset the auto-increment primary key to 0."""
    with connection.cursor() as cursor:
        table_name = model._meta.db_table
        cursor.execute(f"UPDATE sqlite_sequence SET seq = 0 WHERE name='{table_name}'")


# Task 1: Run once a day at 8:00 PM to collect historical data, weekdays only   day_of_week='mon-fri'
@register_job(scheduler, 'cron', id='collect_history_data', hour=12, minute=15, day_of_week='mon-fri')
def collect_history_data():
    try:
        if not collectHistoryData():
            logger.error("Historical collection was incomplete; preserving the existing dataset")
            return 0

        directory_path = os.path.join(os.path.dirname(__file__), 'HistoricalData')
        imported_count = replace_historical_data_from_csv(directory_path)
        logger.info("Replaced historical dataset with %s validated rows", imported_count)
        return imported_count
    except Exception:
        logger.exception("Historical collection or import failed; preserving the existing dataset")
        return 0


# Task 2: Run every half an hour to collect recent data, weekdays only
@register_job(scheduler, 'cron', id='collect_recent_data', minute='*/30', day_of_week='mon-fri')
def collect_recent_data():
    try:
        # collect recent data
        collectRecentData()
        logger.info("[On Schedule] Recent data collected successfully")

        # clear existing data
        RecentData.objects.all().delete()
        reset_autoincrement(RecentData)
        logger.info("[On Schedule] Cleared existing recent data")
    except Exception as e:
        logger.error(f"Error collecting recent data: {e}")

    # import recent data
    recent_data_path = os.path.join(os.path.dirname(__file__), 'RecentData')
    if os.path.exists(recent_data_path):
        try:
            for filename in os.listdir(recent_data_path):
                if filename.endswith('.csv'):
                    file_path = os.path.join(recent_data_path, filename)

                    currency_pair = filename.split('.')[0].split('_')[0]

                    data = pd.read_csv(file_path)

                    for index, row in data.iterrows():
                        currency_pair = currency_pair.split('.')[0]
                        if len(currency_pair) == 6:
                            currency_pair = currency_pair[:3] + '/' + currency_pair[3:]

                        RecentData.objects.create(
                            symbol=currency_pair,
                            date=row['Datetime'],
                            open=row['Open'],
                            high=row['High'],
                            low=row['Low'],
                            close=row['Close']
                        )
            logger.info("Recent data imported successfully")
        except Exception as e:
            logger.error(f"Error importing recent data: {e}")
    else:
        logger.warning(f"Directory {recent_data_path} does not exist")
        
# Task 3: Run every hour to collect training data, weekdays only      
@register_job(scheduler, 'cron', id='collect_training_data', minute=45, day_of_week='mon-fri')
def collect_training_data():
    try:
        # collect training data
        collectTrainingData()
        logger.info("[On Schedule] Training data collected successfully")

    except Exception as e:
        logger.error(f"Error collecting Training data: {e}")

def clear_existing_jobs():
    """Clear persisted scheduler jobs when tables are available."""
    try:
        DjangoJob.objects.all().delete()
    except (OperationalError, ProgrammingError) as exc:
        logger.warning(f"Skip clearing scheduler jobs before migrations: {exc}")

# register events and start the scheduler
register_events(scheduler)
