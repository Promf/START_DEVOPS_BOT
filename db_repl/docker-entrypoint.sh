#!/bin/bash
set -e

if [ "$REPLICATION_MODE" = "standby" ]; then
  if [ ! -f "$PGDATA/standby.signal" ] && [ -z "$(ls -A "$PGDATA")" ]; then
    echo "Запуск pg_basebackup для инициализации standby из мастера $PG_MASTER_HOST:$PG_MASTER_PORT..."
    until pg_isready -h "$PG_MASTER_HOST" -p "$PG_MASTER_PORT" -U "$REPLICATOR_USER"; do
      echo "Ожидание мастера..."
      sleep 2
    done
    pg_basebackup -h "$PG_MASTER_HOST" -p "$PG_MASTER_PORT" -D "$PGDATA" -U "$REPLICATOR_USER" -P -R
    echo "Бэкап завершен, контейнер теперь настроен как standby."
    chown -R postgres:postgres "$PGDATA"
  fi
fi

exec /usr/local/bin/docker-entrypoint.sh "$@"

