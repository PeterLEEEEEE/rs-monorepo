FROM mongo:latest
ENV TZ=Asia/Seoul

COPY docker/mongodb/conf/mongo.conf /etc/mongo/mongod.conf

CMD ["mongod", "--config", "/etc/mongo/mongod.conf"]