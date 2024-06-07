#!/bin/bash

# Функция для обработки ошибок
handle_error() {
    echo "Error: $1"
    exit 1
}

echo "Initializing Change Data Capture (CDC)"
echo "------------------------------------"
echo "      PostgreSQL to ClickHouse"
echo " "
echo " "

# Запуск контейнеров Docker Compose
docker-compose up -d || handle_error "Failed to start Docker Compose."

# Ожидание инициализации Kafka Connect
echo "Waiting for Kafka Connect to start..."
for ((i=0; i<60; i++)); do
    if curl --output /dev/null --silent --head --fail http://localhost:8083; then
        echo "Kafka Connect started successfully."
        break
    else
        printf '.'
        sleep 1
    fi
    if [ $i -eq 29 ]; then
        handle_error "Timeout: Kafka Connect failed to start within 30 seconds."
    fi
done

# Копирование JAR-файла ClickHouse и перезапуск контейнера
docker cp clickhouse-kafka-connect-v1.1.0-confluent.jar etl-connect-1:/kafka/connect || handle_error "Failed to copy ClickHouse JAR file."
docker-compose restart connect || handle_error "Failed to restart Kafka Connect container."


# Ожидание инициализации Kafka Connect
echo "Waiting for Kafka Connect to start..."
for ((i=0; i<60; i++)); do
    if curl --output /dev/null --silent --head --fail http://localhost:8083; then
        echo "Kafka Connect started successfully."
        break
    else
        printf '.'
        sleep 1
    fi
    if [ $i -eq 29 ]; then
        handle_error "Timeout: Kafka Connect failed to start within 30 seconds."
    fi
done

# Регистрация коннектора для PostgreSQL
echo "Registering PostgreSQL connector..."
curl_output=$(curl -sS -X POST -H "Content-Type: application/json" --data @debezium-postgres-connector.json http://localhost:8083/connectors)
echo $curl_output | grep "error_code" && handle_error "Failed to register PostgreSQL connector: $curl_output"
echo "PostgreSQL connector registered successfully."

# Регистрация коннектора ClickHouse
echo "Registering ClickHouse sink connector..."
curl_output=$(curl -sS -X POST -H "Content-Type: application/json" --data @clickhouse-sink-connector.json http://localhost:8083/connectors)
echo $curl_output | grep "error_code" && handle_error "Failed to register ClickHouse connector: $curl_output"
echo "ClickHouse sink connector registered successfully."

# Проверка зарегистрированных коннекторов
echo "Registered connectors:"
curl http://localhost:8083/connectors || handle_error "Failed to get list of registered connectors from Kafka Connect."

echo "CDC initialized successfully."
