FROM aorwall/swe-bench-psf_requests:latest

RUN git -c advice.detachedHead=false checkout bf436ea0a49513bd4e49bb2d1645bd770e470d75

RUN conda create -n psf__requests__2.7 python=3.9 pytest -y

SHELL ["conda", "run", "-n", "psf__requests__2.7", "/bin/bash", "-c"]


RUN python -m pip install .
ENV TESTBED_NAME=psf__requests__2.7

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]