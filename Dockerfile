FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY main.py /app/main.py
COPY templates /app/templates
CMD python3 /app/main.py