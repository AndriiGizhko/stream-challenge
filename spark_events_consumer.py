import json
import socket
from time import sleep

import yaml
from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext


def wait_for_port_to_open(host: str, port: int) -> None:
    """
    Waits for given port to be reachable
        Parameters:
            :param host: host of service
            :param port: port of service
    """
    while port_is_open(host, port) is False:
        print(f"Waiting for service on %s : %s to open".format(host, port))
        sleep(5)


def port_is_open(host: str, port: int) -> bool:
    """
    Checks if port on given host is open
        Parameters:
            :param host: host name
            :param port: port number
        Returns:
            boolean result of check
    """
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = (host, port)
    check_result = a_socket.connect_ex(location)
    if check_result == 0:
        return True
    else:
        return False


def update_function(value: list, state: dict) -> dict:
    """
    Executed for each key state. In case of no updated values returns state with key 'updated' equal True
        Parameters:
            :param value: value of key/value pair
            :param state: state of a key
        Returns:
            state dict
    """
    if state is None:
        state = {"updated": True, "data": []}
    if len(value) > 0:
        data = value[0] + state["data"]
        data = sorted(data, key=lambda x: x["Timestamp"], reverse=True)[:5]
        return {"updated": True, "data": data}
    else:
        return {"updated": False, "data": state["data"]}


def create_spark_context(
    events_stream_host: str, events_stream_port: int, es_write_conf: dict
) -> "StreamingContext":
    """
        Parameters
            :param events_stream_host: host of events stream
            :param events_stream_port: port of events stream
            :param es_write_conf: elastic-search spark write configuration dict
        Returns:
            Streaming Context object
    """
    conf = SparkConf().set(
        "spark.jars", "./jars/elasticsearch-spark-20_2.11-7.16.2.jar"
    )
    sc = SparkContext("local[2]", "Processing Tracking Events", conf=conf)

    ssc = StreamingContext(sc, 1)

    events = ssc.socketTextStream(events_stream_host, events_stream_port)

    try:
        aggregated_events = (
            events.map(lambda x: json.loads(x))
            .map(lambda y: (y["Id"], {"Timestamp": y["Timestamp"], "Url": y["Url"]}))
            .groupByKey()
            .mapValues(list)
        )
    except ValueError as e:
        print("Events aggregation failed: " + str(events) + " with an error: " + str(e))
        raise e

    states = aggregated_events.updateStateByKey(update_function)

    updated_records = states.filter(lambda x: x[1]["updated"] is True).map(
        lambda x: (
            x[0],
            json.dumps({"id": x[0], "last_5_urls": [i["Url"] for i in x[1]["data"]]}),
        )
    )

    updated_records.foreachRDD(
        lambda rdd: rdd.saveAsNewAPIHadoopFile(
            path="-",
            outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
            keyClass="org.apache.hadoop.io.NullWritable",
            valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
            conf=es_write_conf,
        )
    )

    ssc.checkpoint("./checkpointing")
    return ssc


if __name__ == "__main__":
    configuration = yaml.load(
        open("configuration.yml", "r"), Loader=yaml.FullLoader
    ).get("spark")
    wait_for_port_to_open(
        configuration["es_write_conf"]["es.nodes"],
        int(configuration["es_write_conf"]["es.port"]),
    )
    print("ElasticSearch initialised")
    ssc = create_spark_context(
        events_stream_host=configuration["events_stream"]["host"],
        events_stream_port=configuration["events_stream"]["port"],
        es_write_conf=configuration["es_write_conf"],
    )
    ssc.start()
    ssc.awaitTermination()
