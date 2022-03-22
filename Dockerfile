FROM python:3.10

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY *.py ./

ENV INFLUX_URL "http://localhost:8086"
ENV INFLUX_TOKEN ""
ENV GIVENERGY_API_TOKEN ""

CMD python -u influx.py
