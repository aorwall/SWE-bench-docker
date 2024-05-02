FROM aorwall/swe-bench-psf_requests:latest

RUN git -c advice.detachedHead=false checkout 091991be0da19de9108dbe5e3752917fea3d7fdc

RUN conda create -n psf__requests__2.4 python=3.9 pytest -y

SHELL ["conda", "run", "-n", "psf__requests__2.4", "/bin/bash", "-c"]


RUN python -m pip install .
ENV TESTBED_NAME=psf__requests__2.4

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]