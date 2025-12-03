FROM redis:alpine
ENV TZ=Asia/Seoul

COPY docker/redis/conf/redis.conf /usr/local/conf/redis.conf
COPY docker/redis/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]