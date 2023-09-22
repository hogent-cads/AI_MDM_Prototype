FROM almalinux:9.1-minimal

EXPOSE 80/tcp

RUN mkdir /opt/AI_MDM_Prototype
WORKDIR /opt/AI_MDM_Prototype

# Install necessary packages

RUN microdnf install -y java-1.8.0-openjdk-headless procps-ng tar gzip nginx python3 python3-pip gcc python3-devel.x86_64 \
    && microdnf clean all

# Install spark
RUN mkdir --parents external/spark \
    && curl --output spark.tgz https://dlcdn.apache.org/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz \
    && tar --extract --file spark.tgz --directory external/spark --strip-components 1 \
    && rm spark.tgz \
    && rm -r external/spark/examples

# Install zingg
RUN mkdir --parents external/zingg \
    && curl --location --output zingg.tar.gz https://github.com/zinggAI/zingg/releases/download/v0.3.4/zingg-0.3.4-SNAPSHOT-spark-3.1.2.tar.gz \
    && tar --extract --file zingg.tar.gz --directory external/zingg --strip-components 1 \
    && rm zingg.tar.gz \
    && rm -r external/zingg/examples

# Install metanome-utils
RUN mkdir --parents external/metanome-utils \
    && curl --location --output metanome-cli-1.1.0.jar https://github.com/sekruse/metanome-cli/releases/download/v1.1.0/metanome-cli-1.1.0.jar \
    && curl --location --output pyro-distro-1.0-SNAPSHOT-distro.jar https://github.com/HPI-Information-Systems/pyro/releases/download/v1.0/pyro-distro-1.0-SNAPSHOT-distro.jar \
    && mv metanome-cli-1.1.0.jar external/metanome-utils \
    && mv pyro-distro-1.0-SNAPSHOT-distro.jar external/metanome-utils

# Install nginx
RUN mkdir --parents /usr/share/nginx/html/reports \
    && chmod a+rw /usr/share/nginx/html/reports
COPY nginx.conf /etc/nginx/

# Install AI_MDM_Prototype
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir gunicorn gunicorn[gevent] --requirement requirements.txt
COPY --link . /opt/AI_MDM_Prototype

CMD ["./docker-entrypoint.sh"]
