#!/bin/sh

echo 'Starting Redis configuration...'

cp /usr/local/conf/redis.conf /tmp/redis.conf

if [ -n "$REDIS_PASSWORD" ]; then
  echo "Setting password: $REDIS_PASSWORD"
  sed -i "s/^requirepass .*/requirepass $REDIS_PASSWORD/" /tmp/redis.conf
else
  echo 'No password set, removing requirepass line'
  sed -i '/^requirepass/d' /tmp/redis.conf
fi
echo 'Starting Redis server...'
exec redis-server /tmp/redis.conf