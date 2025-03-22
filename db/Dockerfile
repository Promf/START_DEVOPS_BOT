FROM postgres:latest

# Переменные окружения для создания БД
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=123123
ENV POSTGRES_DB=tgbot

# Копируем SQL-скрипт для инициализации
COPY init.sql /docker-entrypoint-initdb.d/

# Копируем конфигурационные файлы в правильную директорию
COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY pg_hba.conf /etc/postgresql/pg_hba.conf

RUN apt update && apt install ssh -y
# Создаём каталог для WAL-логов и даём права
RUN mkdir -p /var/lib/postgresql/wal_archive && \
    chown -R postgres:postgres /var/lib/postgresql/wal_archive

# Даём доступ PostgreSQL к конфигурационным файлам
RUN chown postgres:postgres /etc/postgresql/postgresql.conf /etc/postgresql/pg_hba.conf && \
    chmod 644 /etc/postgresql/postgresql.conf /etc/postgresql/pg_hba.conf

COPY docker-entrypoint.sh /usr/local/bin/custom-entrypoint.sh
RUN chmod +x /usr/local/bin/custom-entrypoint.sh

RUN echo "root:123123" | chpasswd

# Открываем порт PostgreSQL
EXPOSE 5432
EXPOSE 22
ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]
# Запускаем PostgreSQL с указанием конфигурационного файла
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
