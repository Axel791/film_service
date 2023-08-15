CREATE DATABASE IF NOT EXISTS shard;
CREATE DATABASE IF NOT EXISTS replica;

CREATE TABLE shard.kafka_film_timestamp (
      user_id UUID,
      film_id UUID,
      film_timestamp DateTime('Europe/Moscow'),
      event_time DateTime('Europe/Moscow'))
      ENGINE = Kafka('localhost:9092', 'films-timestamps', 'timestamp-viewers-group', 'JSONEachRow');


CREATE MATERIALIZED VIEW consumer TO shard.film_timestamp
      AS SELECT * FROM  shard.kafka_film_timestamp;

CREATE TABLE IF NOT EXISTS shard.film_timestamp (
      user_id UUID,
      film_id UUID,
      film_timestamp DateTime('Europe/Moscow'),
      event_time DateTime('Europe/Moscow'))
      Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/film_timestamp', 'replica_1') PARTITION BY toYYYYMMDD(event_time) ORDER BY user_id;

CREATE TABLE IF NOT EXISTS replica.film_timestamp (
      user_id UUID,
      film_id UUID,
      film_timestamp DateTime('Europe/Moscow'),
      event_time DateTime('Europe/Moscow'))
      Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/film_timestamp', 'replica_2') PARTITION BY toYYYYMMDD(event_time) ORDER BY user_id;

CREATE TABLE IF NOT EXISTS default.film_timestamp (
      user_id UUID,
      film_id UUID,
      film_timestamp DateTime('Europe/Moscow'),
      event_time DateTime('Europe/Moscow')) ENGINE = Distributed('company_cluster', '', film_timestamp, rand());