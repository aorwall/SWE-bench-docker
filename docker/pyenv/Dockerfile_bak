FROM debian:bookworm-slim

ENV PYENV_ROOT="/opt/pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:$PATH"

RUN apt-get update --quiet && \
    apt-get install --yes --no-install-recommends \
        build-essential \
        bzip2 \
        ca-certificates \
        curl \
        git \
        bash \
        gcc \
        gdb \
        g++ \
        lcov \
        libbz2-dev \
        libffi-dev \
        libgdbm-compat-dev \
        libgdbm-dev \
        liblzma-dev \
        libmemcached-dev \
        libncurses-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        lzma-dev \
        make \
        pkg-config \
        tk-dev \
        uuid-dev \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*_dists_*

RUN curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash && \
    pyenv update

WORKDIR /opt
RUN mkdir /opt/logs

COPY swebench_docker swebench_docker
COPY docker/pyenv/entrypoint.sh .

ENTRYPOINT ["/opt/entrypoint.sh"]