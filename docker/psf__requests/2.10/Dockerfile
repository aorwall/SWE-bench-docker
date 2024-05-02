FROM aorwall/swe-bench-psf_requests:latest

RUN git -c advice.detachedHead=false checkout 36453b95b13079296776d11b09cab2567ea3e703

RUN conda create -n psf__requests__2.10 python=3.9 pytest -y

SHELL ["conda", "run", "-n", "psf__requests__2.10", "/bin/bash", "-c"]


RUN python -m pip install .
ENV TESTBED_NAME=psf__requests__2.10

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]