#!/bin/bash
NC_HOST=`cat configuration.yml | shyaml get-value netcat.host`
NC_PORT=`cat configuration.yml | shyaml get-value netcat.port`
ES_HOST=`cat configuration.yml | shyaml get-value elasticsearch.host`
ES_PORT=`cat configuration.yml | shyaml get-value elasticsearch.port`
sudo -H -u elasticsearch /usr/share/elasticsearch/bin/elasticsearch -E network.host=${ES_HOST} -E http.port=${ES_PORT} -d
python spark_events_consumer.py > output_spark.log 2> errors_spark_output.log &

echo 'Generating events'
python generate_tracking_events.py  2> errors_events_generator.log

while true; do cat generated_events.txt | nc -lk -q 5 ${NC_HOST} ${NC_PORT} \
&& curl "http://localhost:9200/tracking_events/_search?pretty=true&q=*:*" \
&& python generate_tracking_events.py 2> errors_events_generator.log; done
