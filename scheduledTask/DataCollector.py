import os, logging
import datetime
import shutil
import uuid
from pathlib import Path
import yfinance as yf


# Configure logging
logger = logging.getLogger('dataCollector')

# Define the Forex ticker (e.g., EURUSD=X for Euro to USD)
# REDERENCE: https://finance.yahoo.com/markets/currencies
EURUSD_ticker = "EURUSD=X"
USDJPY_ticker = "USDJPY=X"
JPYCNY_ticker = "JPYCNY=X"
USDCNY_ticker = "USDCNY=X"
AUDCNY_ticker = "AUDCNY=X"
GBPUSD_ticker = "GBPUSD=X"
EURGBP_ticker = "EURGBP=X"
EURJPY_ticker = "EURJPY=X"
GBPJPY_ticker = "GBPJPY=X"
NZDUSD_ticker = "NZDUSD=X"
gold_ticker = "GC=F"
BITCOIN_ticker = "BTC-USD"

# Get the date when a collection runs, not when this module is imported.
def _today_utc():
    return datetime.datetime.now(datetime.timezone.utc).date()

def collectHistoryData(directory=None):
    """Fetch a complete historical batch into its own directory, or return None."""
    logger.debug("*****************Collecting historical data*****************")

    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent / "HistoricalData"
    directory.mkdir(parents=True, exist_ok=True)
    batch_directory = directory / f".batch-{uuid.uuid4().hex}"
    batch_directory.mkdir()
    end_date = _today_utc()
    tickers = {
        "EURUSD": EURUSD_ticker,
        "USDJPY": USDJPY_ticker,
        "JPYCNY": JPYCNY_ticker,
        "USDCNY": USDCNY_ticker,
        "AUDCNY": AUDCNY_ticker,
        "GBPUSD": GBPUSD_ticker,
        "EURGBP": EURGBP_ticker,
        "EURJPY": EURJPY_ticker,
        "GBPJPY": GBPJPY_ticker,
        "NZDUSD": NZDUSD_ticker,
        "gold": gold_ticker,
        "bitcoin": BITCOIN_ticker,
    }
    failures = []

    for filename, ticker in tickers.items():
        csv_path = batch_directory / f"{filename}.csv"
        temporary_path = batch_directory / f".{filename}.csv.tmp"
        try:
            frame = yf.Ticker(ticker).history(start="2020-01-01", end=end_date, interval="1d")
            if frame.empty:
                raise ValueError("provider returned no historical rows")
            frame.to_csv(temporary_path)
            os.replace(temporary_path, csv_path)
            logger.info("Collected historical data for %s", ticker)
        except Exception as exc:
            failures.append(ticker)
            logger.error("Historical collection failed for %s: %s", ticker, exc)
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                logger.warning("Could not remove incomplete temporary file %s", temporary_path)

    if failures:
        logger.error("Historical collection incomplete; failed providers: %s", ", ".join(failures))
        shutil.rmtree(batch_directory, ignore_errors=True)
        return None
    return batch_directory

def collectRecentData(directory=None):
    """Collect all recent providers into an isolated batch, or return None."""
    logger.debug("*****************Collecting recent data*****************")
    today = _today_utc()
    start_date = today - datetime.timedelta(days=59)

    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent / "RecentData"
    directory.mkdir(parents=True, exist_ok=True)
    batch_directory = directory / f".batch-{uuid.uuid4().hex}"
    batch_directory.mkdir()

    tickers = {
        "EURUSD_recent.csv": EURUSD_ticker,
        "USDJPY_recent.csv": USDJPY_ticker,
        "JPYCNY_recent.csv": JPYCNY_ticker,
        "USDCNY_recent.csv": USDCNY_ticker,
        "AUDCNY_recent.csv": AUDCNY_ticker,
        "GBPUSD_recent.csv": GBPUSD_ticker,
        "EURGBP_recent.csv": EURGBP_ticker,
        "EURJPY_recent.csv": EURJPY_ticker,
        "GBPJPY_recent.csv": GBPJPY_ticker,
        "NZDUSD_recent.csv": NZDUSD_ticker,
        "gold_recent.csv": gold_ticker,
        "bitcoin_recent.csv": BITCOIN_ticker,
    }
    failures = []

    for filename, ticker in tickers.items():
        csv_path = batch_directory / filename
        temporary_path = batch_directory / f".{filename}.tmp"
        try:
            frame = yf.Ticker(ticker).history(start=start_date, end=today, interval="2m")
            if frame.empty:
                raise ValueError("provider returned no recent rows")
            frame.to_csv(temporary_path)
            os.replace(temporary_path, csv_path)
            logger.info("Collected recent data for %s", ticker)
        except Exception as exc:
            failures.append(ticker)
            logger.error("(Recent) Error fetching data for %s: %s", ticker, exc)
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                logger.warning("Could not remove incomplete temporary file %s", temporary_path)

    if failures:
        logger.error("Recent collection incomplete; failed providers: %s", ", ".join(failures))
        shutil.rmtree(batch_directory, ignore_errors=True)
        return None
    return batch_directory

def collectTrainingData():
    logger.debug("*****************Collecting training data*****************")
    # Fetch recent data
    today = _today_utc()
    start_date = today - datetime.timedelta(days=729)

    directory_path = os.path.join(os.path.dirname(__file__), 'TrainingData')
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # get the prediction data for the previous month
    try:
        EURUSD_Training = yf.Ticker(EURUSD_ticker).history(start=start_date, end=today, interval="1h")
        EURUSD_Training.to_csv(directory_path + "/EURUSD_Training.csv")
        logger.info("GOT EURUSD Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {EURUSD_ticker}: {e}")
    
    try:
        USDJPY_Training = yf.Ticker(USDJPY_ticker).history(start=start_date, end=today, interval="1h")
        USDJPY_Training.to_csv(directory_path + "/USDJPY_Training.csv")
        logger.info("GOT USDJPY Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {USDJPY_ticker}: {e}")

    try:
        JPYCNY_Training = yf.Ticker(JPYCNY_ticker).history(start=start_date, end=today, interval="1h")
        JPYCNY_Training.to_csv(directory_path + "/JPYCNY_Training.csv")
        logger.info("GOT JPYCNY Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {JPYCNY_ticker}: {e}")
    
    try:
        USDCNY_Training = yf.Ticker(USDCNY_ticker).history(start=start_date, end=today, interval="1h")
        USDCNY_Training.to_csv(directory_path + "/USDCNY_Training.csv")
        logger.info("GOT USDCNY Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {USDCNY_ticker}: {e}")

    try:
        AUDCNY_Training = yf.Ticker(AUDCNY_ticker).history(start=start_date, end=today, interval="1h")
        AUDCNY_Training.to_csv(directory_path + "/AUDCNY_Training.csv")
        logger.info("GOT AUDCNY Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {AUDCNY_ticker}: {e}")

    try:
        GBPUSD_Training = yf.Ticker(GBPUSD_ticker).history(start=start_date, end=today, interval="1h")
        GBPUSD_Training.to_csv(directory_path + "/GBPUSD_Training.csv")
        logger.info("GOT GBPUSD Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {GBPUSD_ticker}: {e}")

    try:
        EURGBP_Training = yf.Ticker(EURGBP_ticker).history(start=start_date, end=today, interval="1h")
        EURGBP_Training.to_csv(directory_path + "/EURGBP_Training.csv")
        logger.info("GOT EURGBP Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {EURGBP_ticker}: {e}")

    try:
        EURJPY_Training = yf.Ticker(EURJPY_ticker).history(start=start_date, end=today, interval="1h")
        EURJPY_Training.to_csv(directory_path + "/EURJPY_Training.csv")
        logger.info("GOT EURJPY Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {EURJPY_ticker}: {e}")

    try:
        GBPJPY_Training = yf.Ticker(GBPJPY_ticker).history(start=start_date, end=today, interval="1h")
        GBPJPY_Training.to_csv(directory_path + "/GBPJPY_Training.csv")
        logger.info("GOT GBPJPY Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {GBPJPY_ticker}: {e}")

    try:
        NZDUSD_Training = yf.Ticker(NZDUSD_ticker).history(start=start_date, end=today, interval="1h")
        NZDUSD_Training.to_csv(directory_path + "/NZDUSD_Training.csv")
        logger.info("GOT NZDUSD Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {NZDUSD_ticker}: {e}")

    try:
        gold_Training = yf.Ticker(gold_ticker).history(start=start_date, end=today, interval="1h")
        gold_Training.to_csv(directory_path + "/gold_Training.csv")
        logger.info("GOT GOLD Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {gold_ticker}: {e}")

    try:
        bitcoin_Training = yf.Ticker(BITCOIN_ticker).history(start=start_date, end=today, interval="1h")
        bitcoin_Training.to_csv(directory_path + "/bitcoin_Training.csv")
        logger.info("GOT BITCOIN Training")
    except Exception as e:
        logger.error(f"(Training) Error fetching currency pair {BITCOIN_ticker}: {e}")
