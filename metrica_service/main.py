import ast
import logging

import numpy as np
import requests
import pandas as pd
from io import StringIO
import time
import clickhouse_connect
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

COUNTER_ID = 94228816
BASE_URL = f"https://api-metrika.yandex.net/management/v1/counter/{COUNTER_ID}"
OAUTH_TOKEN = "OAuth y0_AgAAAAA8R1a8AAu1wAAAAAEDh525AACFUITpMSZPX5K5_iox11m8io3TEg"


def send_visit_log_request(date1, date2):
    try:
        url = f"{BASE_URL}/logrequests?date1={date1}&date2={date2}&fields=ym:s:visitID,ym:s:parsedParamsKey1,ym:s:parsedParamsKey2,ym:s:parsedParamsKey3,ym:s:parsedParamsKey4,ym:s:parsedParamsKey5,ym:s:clientID,ym:s:ipAddress,ym:s:watchIDs,ym:s:dateTime,ym:s:deviceCategory,ym:s:mobilePhone,ym:s:mobilePhoneModel,ym:s:operatingSystemRoot,ym:s:operatingSystem,ym:s:browser,ym:s:visitDuration&source=visits"
        headers = {
            "Authorization": OAUTH_TOKEN,
        }

        response = requests.post(url, headers=headers)
        response.raise_for_status()  # Проверяем наличие ошибок в запросе
        data = response.json()
        request_id = data["log_request"]["request_id"]
        logging.info(f"Log request {request_id} created successfully")
        return request_id
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while sending log request: {e}")
        raise


def check_log_request_status(request_id):
    try:
        url = f"{BASE_URL}/logrequest/{request_id}"
        headers = {
            "Authorization": OAUTH_TOKEN
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверяем наличие ошибок в запросе
        data = response.json()
        status = data["log_request"]["status"]
        logging.info(f"Log request {request_id} status: {status}")
        return status
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while checking log request status: {e}")
        raise


def get_request_parts(request_id):
    try:
        url = f"{BASE_URL}/logrequest/{request_id}"
        headers = {
            "Authorization": OAUTH_TOKEN
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверяем наличие ошибок в запросе
        data = response.json()
        parts = data["log_request"]["parts"]
        logging.info(f"Log request {request_id} processed in {len(parts)} parts")
        return parts
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while getting log request parts: {e}")
        raise


def download_and_load_parts(request_id, parts):
    try:
        dfs = []
        for part in parts:
            part_number = part["part_number"]
            url = f"{BASE_URL}/logrequest/{request_id}/part/{part_number}/download"
            headers = {
                "Authorization": OAUTH_TOKEN
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем наличие ошибок в запросе
            data = response.text

            df = pd.read_csv(StringIO(data), delimiter='\t', header=0)
            dfs.append(df)
            logging.info(f"Data from part {part_number} of log request {request_id} loaded successfully")

        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    except (requests.exceptions.RequestException, pd.errors.ParserError) as e:
        logging.error(f"Error occurred while downloading and loading log request parts: {e}")
        raise


def clear_request_log(request_id):
    try:
        url = f"{BASE_URL}/logrequest/{request_id}/clean"
        headers = {
            "Authorization": OAUTH_TOKEN
        }

        response = requests.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        status = data["log_request"]["status"]
        logging.info(f"Log request {request_id} cleaned. Status {status}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while cleaning log request: {e}")
        raise


def get_visit_log(date1, date2):
    pass


def get_hit_log(date1, date2):
    pass


def init_and_get_connection():
    pass


def main():
    try:
        request_id = send_visit_log_request(date1='2023-07-01', date2='2024-04-30')
        client = clickhouse_connect.get_client(
            host='i072uzvaty.eu-central-1.aws.clickhouse.cloud',
            port=8443,
            user='default',
            password='spufBNX.UP8Rj',
            secure=True
        )
        while True:
            status = check_log_request_status(request_id)
            if status == "processed":
                parts = get_request_parts(request_id)
                visits_df = download_and_load_parts(request_id, parts)
                print(visits_df)
                visits_df.reset_index(drop=True, inplace=True)
                print(visits_df)
                visits_df.to_csv('df.csv')

                visits_df['ym:s:parsedParamsKey1'] = visits_df['ym:s:parsedParamsKey1'].apply(
                    lambda x: ast.literal_eval(x))
                visits_df['ym:s:parsedParamsKey2'] = visits_df['ym:s:parsedParamsKey2'].apply(
                    lambda x: ast.literal_eval(x))
                visits_df['ym:s:parsedParamsKey3'] = visits_df['ym:s:parsedParamsKey3'].apply(
                    lambda x: ast.literal_eval(x))
                visits_df['ym:s:parsedParamsKey4'] = visits_df['ym:s:parsedParamsKey4'].apply(
                    lambda x: ast.literal_eval(x))
                visits_df['ym:s:parsedParamsKey5'] = visits_df['ym:s:parsedParamsKey5'].apply(
                    lambda x: ast.literal_eval(x))
                visits_df['ym:s:watchIDs'] = visits_df['ym:s:watchIDs'].apply(lambda x: eval(x))
                visits_df['ym:s:dateTime'] = pd.to_datetime(visits_df['ym:s:dateTime'], format='%Y-%m-%d %H:%M:%S')
                visits_df['ym:s:ipAddress'] = visits_df['ym:s:ipAddress'].astype(str)
                visits_df['ym:s:mobilePhone'] = visits_df['ym:s:mobilePhone'].astype(str)
                visits_df['ym:s:mobilePhoneModel'] = visits_df['ym:s:mobilePhoneModel'].astype(str)
                visits_df['ym:s:operatingSystemRoot'] = visits_df['ym:s:operatingSystemRoot'].astype(str)
                visits_df['ym:s:operatingSystem'] = visits_df['ym:s:operatingSystem'].astype(str)
                visits_df['ym:s:browser'] = visits_df['ym:s:browser'].astype(str)

                print(visits_df.dtypes)

                import matplotlib.pyplot as plt

                np.random.seed(42)  # для воспроизводимости результатов
                unique_client_ids = visits_df['ym:s:clientID'].unique()
                random_roles = np.random.choice(['Администратор', 'Обычный пользователь', 'Преподаватель', 'Технический специалист'], size=len(unique_client_ids))
                role_mapping = dict(zip(unique_client_ids, random_roles))
                visits_df['role'] = visits_df['ym:s:clientID'].map(role_mapping)

                visits_df['ym:s:dateTime'] = pd.to_datetime(visits_df['ym:s:dateTime'])

                # Определим периоды времени (например, еженедельно или ежемесячно)
                visits_df['week'] = visits_df['ym:s:dateTime'].dt.to_period('W')
                visits_df['month'] = visits_df['ym:s:dateTime'].dt.to_period('M')
                visits_df.to_csv('visits-df.csv')
                roles = visits_df.groupby('role').apply(list)

                # Посчитаем метрики вовлеченности пользователей для каждой группы и периода времени
                engagement_metrics = visits_df.groupby(['role', 'week'])['ym:s:visitID'].count().reset_index()

                # Визуализация данных
                for role in roles.unique():
                    role_data = engagement_metrics[engagement_metrics['role'] == role]
                    plt.plot(role_data['week'], role_data['ym:s:visitID'], label=role)

                plt.xlabel('Неделя')
                plt.ylabel('Количество взаимодействий')
                plt.title('Метрика вовлеченности пользователей по неделям')
                plt.legend()
                plt.show()

                client.insert_df(table='default.metrica_visits',
                                 database='metrica_data',
                                 df=visits_df,
                                 column_names=['visitID', 'parsedParamsKey1', 'parsedParamsKey2', 'parsedParamsKey3',
                                               'parsedParamsKey4', 'parsedParamsKey5', 'clientID', 'ipAddress',
                                               'watchIDs', 'dateTime', 'deviceCategory', 'mobilePhone',
                                               'mobilePhoneModel', 'operatingSystemRoot', 'operatingSystem', 'browser',
                                               'visitDuration'],
                                 column_type_names=['UInt64', 'Array(String)', 'Array(String)', 'Array(String)',
                                                    'Array(String)', 'Array(String)', 'UInt64', 'String',
                                                    'Array(UInt64)', 'DateTime', 'UInt64', 'String', 'String',
                                                    'String', 'String', 'String', 'UInt32'])
                break
            time.sleep(10)

        client.close()
        clear_request_log(request_id)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()
