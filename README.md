---

# Events Streaming Assignment

### Summary

Dockerized Application that deploys and orchestrates: 

- NetCat
- Spark
- ElasticSearch

using Python as simulation of event streaming processing and aggregation using Spark. 

Application consists of:

- Event generator script  `generate_tracking_events.py`
- Spark consumer script `spark_events_consumer.py`
- bash script `launch_script.sh`
- configuration file `configuration.yml`
- Unit tests `tests/`

Application can be run locally using Docker via: 
 `docker build --rm -t stream-assignment .`
 `docker run -t -i stream-assignment`

During run new events are generated and consumed with results written to ElasticSearch cluster.
In console data saved to ElasticSearch index is periodically printed. 

Important note: this applcation docerizes deployment of several services in one image for demonstation
purposes and to simplify local run. This version is not ready for deployment into production.  

### Details

#### Event generator script
Generates file `generated_events.txt` with events of format {'Id': 1, 'Url': 'url', Timestamp: 1}
based on configured parameters in configuration.yml. Xml of configured homepage address is used in order
to generate more realistic urls. 

#### Spark consumer script
Requires ElasticSearch cluster being reachable on configured port. Waits for port being open before launching.
Reads from configured port, aggregates and persists in state events data and write into ElasticSearch index.
In current implementation state is persist in memory and does not use state store. Timestamp
of events persists in state as well in order to correctly keep data only from 5 latest events. 
Elasticsearch index updated only with records that changed state in streaming iteration. 

State data is persisted in format of dictionaries list for better code readability. Tuples usage would improve performance. 
#### Bash script 

Launches Elasticsearch cluster on configured host and port together with Spark consumer script in background mode.
Generates tracking events file and then runs bash loop of sending generated events to NetCat, printing
in console ElasticSearch index data and generating new events. 


#### Further possible improvements

- increase unittests coverage
- integrating required logging strategy and streamline logs to required logs monitoring tool
- implement required strategy for handling malformed events without breaking consumer script
