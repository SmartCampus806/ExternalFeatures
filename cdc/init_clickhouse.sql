ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET max_replication_slots = 1;
ALTER SYSTEM SET max_wal_senders = 1;

CREATE TABLE IF NOT EXISTS public.test_table (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  value FLOAT
);

DO
$$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'debezium') THEN
    CREATE USER debezium WITH REPLICATION PASSWORD 'debezium';
  END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE test_db TO debezium;
