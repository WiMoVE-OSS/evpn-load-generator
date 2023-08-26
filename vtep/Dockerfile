
FROM ubuntu:22.04
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install python3 \
    iproute2 iputils-ping \
    git autoconf automake libtool make libreadline-dev texinfo \
    pkg-config libpam0g-dev libjson-c-dev bison flex \
    libc-ares-dev python3-dev python3-sphinx \
    install-info build-essential libsnmp-dev perl \
    libcap-dev python2 libelf-dev libunwind-dev \
    protobuf-c-compiler libprotobuf-c-dev \
    libyang2 libyang2-dev -y && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN groupadd -r -g 92 frr && \
    groupadd -r -g 85 frrvty && \
    adduser --system --ingroup frr --home /var/run/frr/ --gecos "FRR suite" --shell /sbin/nologin frr && \
    usermod -a -G frrvty frr

RUN git clone https://github.com/WiMoVE-OSS/frr.git && \
    cd frr && \
    git checkout bgp-routing-target-constraints && \
    ./bootstrap.sh && \
    ./configure \
    --prefix=/usr \
    --includedir=\${prefix}/include \
    --bindir=\${prefix}/bin \
    --sbindir=\${prefix}/lib/frr \
    --libdir=\${prefix}/lib/frr \
    --libexecdir=\${prefix}/lib/frr \
    --localstatedir=/var/run/frr \
    --sysconfdir=/etc/frr \
    --with-moduledir=\${prefix}/lib/frr/modules \
    --enable-configfile-mask=0640 \
    --enable-logfile-mask=0640 \
    --enable-snmp=agentx \
    --enable-multipath=64 \
    --enable-user=frr \
    --enable-group=frr \
    --enable-vty-group=frrvty \
    --with-pkg-git-version \
    --with-pkg-extra-version=-MyOwnFRRVersion && \
    make -j "$(nproc)" && \
    make install

ENV MIN_VNI=1
ENV MAX_VNI=20
ENV VTEP_ID=1
ENV watchfrr_debug=yes
COPY frr/* /etc/frr/
COPY test.py /test.py
CMD ["python3", "/test.py"]
