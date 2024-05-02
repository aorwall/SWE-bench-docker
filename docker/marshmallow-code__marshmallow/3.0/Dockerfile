FROM aorwall/swe-bench-marshmallow-code_marshmallow:latest

RUN git -c advice.detachedHead=false checkout 8b3a32614fd4a74e93e9a63a042e74c1fea34466

RUN conda create -n marshmallow-code__marshmallow__3.0 python=3.9  -y

SHELL ["conda", "run", "-n", "marshmallow-code__marshmallow__3.0", "/bin/bash", "-c"]


RUN pip install -e '.[dev]'
ENV TESTBED_NAME=marshmallow-code__marshmallow__3.0

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]