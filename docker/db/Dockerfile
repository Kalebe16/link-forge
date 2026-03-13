FROM postgres:16

COPY db/dbconfig.yml dbconfig.yml
COPY db/migrations migrations

RUN apt update \
    && apt install -y sql-migrate \
    && apt clean

CMD ["sh", "-c", "docker-entrypoint.sh postgres & until pg_isready -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\"; do sleep 1; done; sleep 2; sql-migrate up -config=./dbconfig.yml -env=default; wait"]
