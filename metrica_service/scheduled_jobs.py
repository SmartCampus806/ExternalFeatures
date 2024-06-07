import schedule
import time

from api import get_df_logs


def scheduled_api_request():
    schedule.every().day.at("00:00").do(get_df_logs, '2024-04-29', '2024-04-30',
                                'ym:s:visitID,ym:s:parsedParamsKey1,ym:s:parsedParamsKey2',
                                'visits')

    while True:
        schedule.run_pending()
        time.sleep(1)
