FROM postgres:latest
COPY docker-entrypoint.sh /usr/local/bin/custom-entrypoint.sh
RUN chmod +x /usr/local/bin/custom-entrypoint.sh
COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY pg_hba.conf /etc/postgresql/pg_hba.conf
ENV REPLICATION_MODE=standby
ENV PG_MASTER_HOST=db
ENV PG_MASTER_PORT=5432
ENV REPLICATOR_USER=postgres
ENV REPLICATOR_PASSWORD=123123
ENV PGPASSWORD=123123
RUN chown postgres:postgres /etc/postgresql/postgresql.conf /etc/postgresql/pg_hba.conf && \ 
	chmod 644 /etc/postgresql/postgresql.conf /etc/postgresql/pg_hba.conf
RUN chmod -R 0700 /var/lib/postgresql/data
ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
