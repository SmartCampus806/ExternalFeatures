import time
from io import StringIO

import pandas as pd
import requests

import yaml


class YandexMetrikaAPI:
    def __init__(self):
        """
        Инициализация класса для работы с API Яндекс.Метрики.
        Параметры находятся в config.yaml

        yandex_metrica.token
        yandex_metrica.counter_id
        yandex_metrica.base_url
        """
        with open('config.yaml') as f:
            config = yaml.safe_load(f)
        self.token = config["yandex_metrica"]["token"]
        self.counter_id = config["yandex_metrica"]["counter_id"]
        self.base_url = config["yandex_metrica"]["base_url"]

    def create_logs_task(self, date1, date2, fields, source) -> int:
        """
        Создание задачи на получение логов в API Яндекс.Метрики.

        Параметры:
            :param date1	Первый день.
            :param date2	Последний день (не может быть текущим днем).
            :param fields	Список полей через запятую.
            :param source	Источник логов.
                Допустимые значения:
                hits — просмотры.
                visits — визиты.

        Возвращает:
            int: Идентификатор созданной задачи request_id.
        """
        headers = {"Authorization": f"OAuth {self.token}"}
        response = requests.post(f"{self.base_url}/management/v1/counter/{self.counter_id}/logrequests?"
                                 f"date1={date1}&"
                                 f"date2={date2}&"
                                 f"fields={fields}&"
                                 f"source={source}",
                                 headers=headers)

        response.raise_for_status()
        return response.json()["log_request"]["request_id"]

    def check_task_status(self, request_id):
        """
        Проверка статуса задачи в API Яндекс.Метрики.

        Параметры:
            request_id (uint): Идентификатор задачи.

        Возвращает:
            dict: Статус задачи.
        """
        headers = {"Authorization": f"OAuth {self.token}"}
        response = requests.get(f"{self.base_url}/management/v1/counter/{self.counter_id}/logrequest/{request_id}/",
                                headers=headers)
        response.raise_for_status()
        if response.json()["log_request"]["status"] == 'processed':
            return {
                "status": response.json()["log_request"]["status"],
                "parts": response.json()["log_request"]["parts"]
            }
        return {"status": response.json()["log_request"]["status"]}

    def get_processed_logs(self, request_id, parts):
        dfs = []
        for part in parts:
            part_number = part["part_number"]

            headers = {"Authorization": f"OAuth {self.token}"}
            response = requests.get(f"{self.base_url}/management/v1/counter/{self.counter_id}/logrequest/"
                                    f"{request_id}/part/{part_number}/download",
                                    headers=headers)
            response.raise_for_status()
            dfs.append(pd.read_csv(StringIO(response.text), delimiter='\t', header=0))
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df


def get_df_logs(date1, date2, fields, source):
    """
    Запуск процесса получения данных из LogsAPI Яндекс.Метрики.
    """
    api = YandexMetrikaAPI()
    request_id = api.create_logs_task(date1, date2, fields, source)
    print(request_id)
    while True:
        task_status = api.check_task_status(request_id)
        if task_status['status'] == "processed":
            print(task_status)
            break
        time.sleep(10)
    return api.get_processed_logs(request_id, task_status['parts'])
