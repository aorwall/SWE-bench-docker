FROM aorwall/swe-bench-pytest-dev_pytest:latest

RUN git -c advice.detachedHead=false checkout d5843f89d3c008ddcb431adbc335b080a79e617e

RUN conda create -n pytest-dev__pytest__4.6 python=3.9  -y

SHELL ["conda", "run", "-n", "pytest-dev__pytest__4.6", "/bin/bash", "-c"]


RUN pip install atomicwrites==1.4.1 attrs==23.1.0 more-itertools==10.1.0 importlib-metadata==1.6.0 packaging==23.1 pluggy==0.13.1 py==1.11.0 six==1.16.0 wcwidth==0.2.6

RUN pip install -e .
ENV TESTBED_NAME=pytest-dev__pytest__4.6

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]