FROM aorwall/swe-bench-psf_requests:latest

RUN git -c advice.detachedHead=false checkout a0df2cbb10419037d11d04352b3175405ab52941

RUN conda create -n psf__requests__0.14 python=3.9 pytest -y

SHELL ["conda", "run", "-n", "psf__requests__0.14", "/bin/bash", "-c"]


RUN python -m pip install .
ENV TESTBED_NAME=psf__requests__0.14

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]