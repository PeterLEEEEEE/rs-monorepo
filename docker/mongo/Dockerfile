FROM mongo:7
ENV TZ=Asia/Seoul

COPY conf/mongo.conf /etc/mongo/mongod.conf

CMD ["mongod", "--config", "/etc/mongo/mongod.conf"]