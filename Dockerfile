FROM python:3.6


# Install dependencies
RUN apt-get update -y \
&&  apt-get install wget -y \
&&  apt-get install -y openjdk-11-jre-headless \
&& apt-get install -y sudo \
&& apt-get install -y netcat-openbsd \
&& apt-get install coreutils

# Copy files to image
COPY . /root
COPY checkpointing /root/checkpointing
COPY tests /root/tests
COPY jars /root/jars

# Install ElasticSearch
RUN wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.5.1-amd64.deb --no-check-certificate
RUN groupadd -g 1000 -f elasticsearch && id -u elasticsearch &>/dev/null || useradd elasticsearch -r -m
RUN dpkg -i ./elasticsearch-7.5.1-amd64.deb

# Install Python dependencies
RUN pip install -r /root/requirements.txt


WORKDIR /root

# Run unit tests
RUN python -m pytest tests/

CMD ["./launch_script.sh"]


