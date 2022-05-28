FROM python

RUN python3 -m pip install redis

RUN apt-get update && apt-get install -y \
   net-tools \
   iputils-ping \
   iproute2

COPY app.py /