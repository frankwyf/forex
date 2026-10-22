import logging
import shutil
from django_apscheduler.models import DjangoJob
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job, register_events
from .DataCollector import collectHistoryData, collectRecentData, collectTrainingData
from .importers import replace_historical_data_from_csv, replace_recent_data_from_csv
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger('scheduler')

# init scheduler
scheduler = BackgroundScheduler(timezone="UTC", job_defaults={
    "max_instances": 1, "coalesce": True, "misfire_grace_time": 300,
})
# add DjangoJobStore to the scheduler
scheduler.add_jobstore(DjangoJobStore(), "default")

# Historical data: weekdays at 12:15 UTC. Registration does not start a worker.
@register_job(scheduler, 'cron', id='collect_history_data', hour=12, minute=15, day_of_week='mon-fri')
def collect_history_data():
    batch_directory = None
    try:
        batch_directory = collectHistoryData()
        if not batch_directory:
            logger.error("Historical collection was incomplete; preserving the existing dataset")
            return 0

        imported_count = replace_historical_data_from_csv(batch_directory)
        logger.info("Replaced historical dataset with %s validated rows", imported_count)
        return imported_count
    except Exception:
        logger.exception("Historical collection or import failed; preserving the existing dataset")
        return 0
    finally:
        if batch_directory:
            shutil.rmtree(batch_directory, ignore_errors=True)


# Task 2: Run every half an hour to collect recent data, weekdays only
@register_job(scheduler, 'cron', id='collect_recent_data', minute='*/30', day_of_week='mon-fri')
def collect_recent_data():
    batch_directory = None
    try:
        batch_directory = collectRecentData()
        if not batch_directory:
            logger.error("Recent collection was incomplete; preserving the existing dataset")
            return 0

        imported_count = replace_recent_data_from_csv(batch_directory)
        logger.info("Replaced recent dataset with %s validated rows", imported_count)
        return imported_count
    except Exception:
        logger.exception("Recent collection or import failed; preserving the existing dataset")
        return 0
    finally:
        if batch_directory:
            shutil.rmtree(batch_directory, ignore_errors=True)
        
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

# Register listeners only. A web worker must never start the scheduler implicitly.
register_events(scheduler)
