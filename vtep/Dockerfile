FROM ubuntu:22.10
RUN apt-get update && apt-get install frr python3 -y && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV MIN_VNI=1
ENV MAX_VNI=20
ENV VTEP_ID=1
COPY frr/* /etc/frr/
COPY test.py /test.py
CMD ["python3", "/test.py"]
