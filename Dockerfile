# FROM almalinux:9.1-minimal
FROM almalinux:9.1

EXPOSE 80/tcp

RUN mkdir /opt/AI_MDM_Prototype
WORKDIR /opt/AI_MDM_Prototype

# Install spark
RUN dnf install -y java-1.8.0-openjdk
RUN mkdir --parents external/spark
RUN curl --output spark.tgz https://dlcdn.apache.org/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz
RUN tar --extract --file spark.tgz --directory external/spark --strip-components 1

# Install zingg
RUN mkdir --parents external/zingg
RUN curl --location --output zingg.tar.gz https://github.com/zinggAI/zingg/releases/download/v0.3.4/zingg-0.3.4-SNAPSHOT-spark-3.1.2.tar.gz
RUN tar --extract --file zingg.tar.gz --directory external/zingg --strip-components 1

# Install nginx
RUN dnf install -y nginx
RUN mkdir --parents /usr/share/nginx/html/reports
RUN chmod a+rw /usr/share/nginx/html/reports
COPY nginx.conf /etc/nginx/

# Install AI_MDM_Prototype
RUN dnf install -y python3 python3-pip gcc
RUN pip3 install gunicorn gunicorn[gevent]
COPY requirements.txt requirements.txt
RUN pip3 install --requirement requirements.txt
COPY --link . /opt/AI_MDM_Prototype

CMD ["./docker-entrypoint.sh"]