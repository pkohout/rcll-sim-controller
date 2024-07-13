FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip curl
RUN curl -LO https://dl.k8s.io/release/v1.30.0/bin/linux/amd64/kubectl && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY main.py /app/main.py
COPY templates /app/templates
CMD python3 /app/main.py