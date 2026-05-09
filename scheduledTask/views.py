import logging, os
import pandas as pd
from .models import HistoricalData, RecentData
from django_apscheduler.models import DjangoJob
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job, register_events
from .DataCollector import collectHistoryData, collectRecentData, collectTrainingData
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
        # Collect historical data
        collectHistoryData()
        logger.info("[On Schedule] Historical data collected successfully")

        # Clear existing data
        HistoricalData.objects.all().delete()
        reset_autoincrement(HistoricalData)
        logger.info("[On Schedule] Cleared existing historical data")
    except Exception as e:
        logger.error(f"Error collecting historical data: {e}")
        
    # Define the directory containing historical data
    directory_path = os.path.join(os.path.dirname(__file__), 'HistoricalData')

    # Check if the directory exists
    if os.path.exists(directory_path):
        try:
            # Iterate over each file in the directory
            for filename in os.listdir(directory_path):
                if filename.endswith('.csv'):
                    file_path = os.path.join(directory_path, filename)

                    # Extract the currency pair from the filename (assuming the format is like 'EURUSD.csv')
                    currency_pair = filename.split('.')[0]

                    # Read the CSV file
                    data = pd.read_csv(file_path)

                    # Iterate over the rows and save them to the database
                    for index, row in data.iterrows():
                        # get currency pair from filename, but without the '.csv' extension
                        # and add a / between the two currencies
                        currency_pair = currency_pair.split('.')[0]
                        if len(currency_pair) == 6:
                            currency_pair = currency_pair[:3] + '/' + currency_pair[3:]
                                    
                        HistoricalData.objects.create(
                            symbol=currency_pair,
                            date=row['Date'],
                            open=row['Open'],
                            high=row['High'],
                            low=row['Low'],
                            close=row['Close']
                        )
            logger.info("Historical Data imported successfully")
        except Exception as e:
            logger.error(f"Error importing data: {e}")
    else:
        logger.warning(f"Directory {directory_path} does not exist")


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