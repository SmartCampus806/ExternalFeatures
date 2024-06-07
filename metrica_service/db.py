import clickhouse_connect
import yaml


class ClickHouseDB:
    def __init__(self, config_file):
        with open(config_file) as f:
            config = yaml.safe_load(f)
        self.__host = config["clickhouse"]["host"]
        self.__port = config["clickhouse"]["port"]
        self.__user = config["clickhouse"]["user"]
        self.__password = config["clickhouse"]["password"]
        self.__database = config["clickhouse"]["database"]

        self.client = clickhouse_connect.get_client(host=self.__host,
                                                    port=self.__port,
                                                    user=self.__user,
                                                    password=self.__password,
                                                    secure=True)

    def insert_data(self, data):
        pass

    def __del__(self):
        self.client.close()
