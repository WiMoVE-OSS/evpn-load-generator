FROM ubuntu:22.10
ENV MIN_VNI=1
ENV MAX_VNI=20
RUN apt update && apt install frr python3
COPY frr/* /etc/frr/
COPY test.py /test.py
CMD ["python3", "/test.py"]
