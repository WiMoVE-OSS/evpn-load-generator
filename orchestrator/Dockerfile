FROM ubuntu:22.10
RUN apt-get update && apt-get install -y python3 python3-numpy && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV MIN_VTEP_ID=1
ENV MAX_VTEP_ID=2
COPY *.py /app/
WORKDIR /app
CMD ["python3", "main.py"]