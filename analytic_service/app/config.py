import yaml
import clickhouse_connect


def load_config():
    with open("../config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
    return config


def get_clickhouse_client():
    config = load_config()
    clickhouse_config = config["clickhouse"]
    client = clickhouse_connect.get_client(
        host=clickhouse_config["host"],
        port=clickhouse_config["port"],
        user=clickhouse_config["user"],
        password=clickhouse_config["password"],
        secure=clickhouse_config["secure"]
    )
    return client
