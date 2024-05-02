FROM aorwall/swe-bench-psf_requests:latest

RUN git -c advice.detachedHead=false checkout 3eb69be879063de4803f7f0152b83738a1c95ca4

RUN conda create -n psf__requests__2.3 python=3.9 pytest -y

SHELL ["conda", "run", "-n", "psf__requests__2.3", "/bin/bash", "-c"]


RUN python -m pip install .
ENV TESTBED_NAME=psf__requests__2.3

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]