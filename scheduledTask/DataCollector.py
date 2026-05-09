import os, logging
import datetime
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

# get today's date
today = datetime.datetime.now().date()

def collectHistoryData():
    logger.debug("*****************Collecting historical data*****************")

    directory_path = os.path.join(os.path.dirname(__file__), 'HistoricalData')
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    try:
        # Fetch current data
        EURUSD_current = yf.Ticker(EURUSD_ticker).history(start="2020-01-01", end=today, interval="1d")
        EURUSD_current.to_csv(directory_path + "/EURUSD.csv")
        logger.info("GOT EURUSD Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {EURUSD_ticker}: {e}")
    
    try:
        USDJPY_current = yf.Ticker(USDJPY_ticker).history(start="2020-01-01", end=today, interval="1d")
        USDJPY_current.to_csv(directory_path + "/USDJPY.csv")
        logger.info("GOT USDJPY Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {USDJPY_ticker}: {e}")
    
    try:
        JPYCNY_current = yf.Ticker(JPYCNY_ticker).history(start="2020-01-01", end=today, interval="1d")
        JPYCNY_current.to_csv(directory_path + "/JPYCNY.csv")
        logger.info("GOT JPYCNY Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {JPYCNY_ticker}: {e}")
    
    try:
        USDCNY_current = yf.Ticker(USDCNY_ticker).history(start="2020-01-01", end=today, interval="1d")
        USDCNY_current.to_csv(directory_path + "/USDCNY.csv")
        logger.info("GOT USDCNY Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {USDCNY_ticker}: {e}")
    
    try:
        AUDCNY_current = yf.Ticker(AUDCNY_ticker).history(start="2020-01-01", end=today, interval="1d")
        AUDCNY_current.to_csv(directory_path + "/AUDCNY.csv")
        logger.info("GOT AUDCNY Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {AUDCNY_ticker}: {e}")
    
    try:
        GBPUSD_current = yf.Ticker(GBPUSD_ticker).history(start="2020-01-01", end=today, interval="1d")
        GBPUSD_current.to_csv(directory_path + "/GBPUSD.csv")
        logger.info("GOT GBPUSD Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {GBPUSD_ticker}: {e}")

    try:
        EURGBP_current = yf.Ticker(EURGBP_ticker).history(start="2020-01-01", end=today, interval="1d")
        EURGBP_current.to_csv(directory_path + "/EURGBP.csv")
        logger.info("GOT EURGBP Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {EURGBP_ticker}: {e}")
    
    try:
        EURJPY_current = yf.Ticker(EURJPY_ticker).history(start="2020-01-01", end=today, interval="1d")
        EURJPY_current.to_csv(directory_path + "/EURJPY.csv")
        logger.info("GOT EURJPY Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {EURJPY_ticker}: {e}")

    try:
        GBPJPY_current = yf.Ticker(GBPJPY_ticker).history(start="2020-01-01", end=today, interval="1d")
        GBPJPY_current.to_csv(directory_path + "/GBPJPY.csv")
        logger.info("GOT GBPJPY Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {GBPJPY_ticker}: {e}")
    
    try:
        NZDUSD_current = yf.Ticker(NZDUSD_ticker).history(start="2020-01-01", end=today, interval="1d")
        NZDUSD_current.to_csv(directory_path + "/NZDUSD.csv")
        logger.info("GOT NZDUSD Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {NZDUSD_ticker}: {e}")

    try:
        gold_current = yf.Ticker(gold_ticker).history(start="2020-01-01", end=today, interval="1d")
        gold_current.to_csv(directory_path + "/gold.csv")
        logger.info("GOT GOLD Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {gold_ticker}: {e}")
    
    try:
        bitcoin_current = yf.Ticker(BITCOIN_ticker).history(start="2020-01-01", end=today, interval="1d")
        bitcoin_current.to_csv(directory_path + "/bitcoin.csv")
        logger.info("GOT BITCOIN Historical")
    except Exception as e:
        logger.error(f"(Historical) Error fetching currency pair {BITCOIN_ticker}: {e}")


def collectRecentData():
    logger.debug("*****************Collecting recent data*****************")
    # Fetch recent data
    start_date = today - datetime.timedelta(days=59)

    directory_path = os.path.join(os.path.dirname(__file__), 'RecentData')
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # get the prediction data for the previous month
    try:
        EURUSD_recent = yf.Ticker(EURUSD_ticker).history(start=start_date, end=today, interval="2m")
        EURUSD_recent.to_csv(directory_path + "/EURUSD_recent.csv")
        logger.info("GOT EURUSD RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {EURUSD_ticker}: {e}")
    
    try:
        USDJPY_recent = yf.Ticker(USDJPY_ticker).history(start=start_date, end=today, interval="2m")
        USDJPY_recent.to_csv(directory_path + "/USDJPY_recent.csv")
        logger.info("GOT USDJPY RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {USDJPY_ticker}: {e}")

    try:
        JPYCNY_recent = yf.Ticker(JPYCNY_ticker).history(start=start_date, end=today, interval="2m")
        JPYCNY_recent.to_csv(directory_path + "/JPYCNY_recent.csv")
        logger.info("GOT JPYCNY RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {JPYCNY_ticker}: {e}")
    
    try:
        USDCNY_recent = yf.Ticker(USDCNY_ticker).history(start=start_date, end=today, interval="2m")
        USDCNY_recent.to_csv(directory_path + "/USDCNY_recent.csv")
        logger.info("GOT USDCNY RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {USDCNY_ticker}: {e}")

    try:
        AUDCNY_recent = yf.Ticker(AUDCNY_ticker).history(start=start_date, end=today, interval="2m")
        AUDCNY_recent.to_csv(directory_path + "/AUDCNY_recent.csv")
        logger.info("GOT AUDCNY RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {AUDCNY_ticker}: {e}")

    try:
        GBPUSD_recent = yf.Ticker(GBPUSD_ticker).history(start=start_date, end=today, interval="2m")
        GBPUSD_recent.to_csv(directory_path + "/GBPUSD_recent.csv")
        logger.info("GOT GBPUSD RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {GBPUSD_ticker}: {e}")

    try:
        EURGBP_recent = yf.Ticker(EURGBP_ticker).history(start=start_date, end=today, interval="2m")
        EURGBP_recent.to_csv(directory_path + "/EURGBP_recent.csv")
        logger.info("GOT EURGBP RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {EURGBP_ticker}: {e}")

    try:
        EURJPY_recent = yf.Ticker(EURJPY_ticker).history(start=start_date, end=today, interval="2m")
        EURJPY_recent.to_csv(directory_path + "/EURJPY_recent.csv")
        logger.info("GOT EURJPY RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {EURJPY_ticker}: {e}")

    try:
        GBPJPY_recent = yf.Ticker(GBPJPY_ticker).history(start=start_date, end=today, interval="2m")
        GBPJPY_recent.to_csv(directory_path + "/GBPJPY_recent.csv")
        logger.info("GOT GBPJPY RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {GBPJPY_ticker}: {e}")

    try:
        NZDUSD_recent = yf.Ticker(NZDUSD_ticker).history(start=start_date, end=today, interval="2m")
        NZDUSD_recent.to_csv(directory_path + "/NZDUSD_recent.csv")
        logger.info("GOT NZDUSD RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {NZDUSD_ticker}: {e}")

    try:
        gold_recent = yf.Ticker(gold_ticker).history(start=start_date, end=today, interval="2m")
        gold_recent.to_csv(directory_path + "/gold_recent.csv")
        logger.info("GOT GOLD RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {gold_ticker}: {e}")

    try:
        bitcoin_recent = yf.Ticker(BITCOIN_ticker).history(start=start_date, end=today, interval="2m")
        bitcoin_recent.to_csv(directory_path + "/bitcoin_recent.csv")
        logger.info("GOT BITCOIN RECENT")
    except Exception as e:
        logger.error(f"(Recent) Error fetching currency pair {BITCOIN_ticker}: {e}")

def collectTrainingData():
    logger.debug("*****************Collecting training data*****************")
    # Fetch recent data
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