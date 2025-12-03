FROM redis:7-alpine
ENV TZ=Asia/Seoul

COPY conf/redis.conf /usr/local/conf/redis.conf
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]