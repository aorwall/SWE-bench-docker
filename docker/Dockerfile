FROM debian:bookworm-slim

ARG TARGETARCH

# Install third party tools
RUN apt-get update && \
    apt-get install -y bash gcc git jq wget g++ make libffi-dev build-essential python3.11 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create new user
RUN useradd -ms /bin/bash swe-bench
USER swe-bench
WORKDIR /home/swe-bench
RUN chown -R swe-bench:swe-bench /home/swe-bench

# Setup Conda
ENV PATH="/home/swe-bench/miniconda3/bin:${PATH}"

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py311_24.3.0-0-Linux-x86_64.sh -O ~/miniconda.sh && \
    mkdir ~/.conda && \
    bash miniconda.sh -b && \
    rm ~/miniconda.sh

# Initialize Conda
RUN conda --version \
    && conda init bash \
    && conda config --append channels conda-forge
