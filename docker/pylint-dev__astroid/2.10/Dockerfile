FROM aorwall/swe-bench-pylint-dev_astroid:latest

RUN git -c advice.detachedHead=false checkout da745538c7236028a22cdf0405f6829fcf6886bc

RUN conda create -n pylint-dev__astroid__2.10 python=3.9  -y

SHELL ["conda", "run", "-n", "pylint-dev__astroid__2.10", "/bin/bash", "-c"]


RUN pip install pytest lazy_object_proxy==1.9.0 wrapt==1.13.3 typing-extensions==4.8.0 setuptools==68.0.0

RUN pip install -e .
ENV TESTBED_NAME=pylint-dev__astroid__2.10

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]