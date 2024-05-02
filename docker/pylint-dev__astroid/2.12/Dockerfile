FROM aorwall/swe-bench-pylint-dev_astroid:latest

RUN git -c advice.detachedHead=false checkout 52f6d2d7722db383af035be929f18af5e9fe8cd5

RUN conda create -n pylint-dev__astroid__2.12 python=3.9  -y

SHELL ["conda", "run", "-n", "pylint-dev__astroid__2.12", "/bin/bash", "-c"]


RUN pip install pytest lazy_object_proxy==1.9.0 wrapt==1.15.0 typing-extensions==4.8.0

RUN pip install -e .
ENV TESTBED_NAME=pylint-dev__astroid__2.12

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]