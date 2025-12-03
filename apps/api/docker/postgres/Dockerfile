FROM pgvector/pgvector:pg18
ENV TZ=Asia/Seoul
COPY docker/postgres/conf/postgres.conf /etc/postgres/postgres.conf

COPY docker/postgres/init/ /docker-entrypoint-initdb.d/

CMD ["postgres", "-c", "config_file=/etc/postgres/postgres.conf"]