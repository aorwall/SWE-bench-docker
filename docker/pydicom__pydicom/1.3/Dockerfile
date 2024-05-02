FROM aorwall/swe-bench-pydicom_pydicom:latest

RUN git -c advice.detachedHead=false checkout 7241f5d9db0de589b230bb84212fbb643a7c86c3

RUN conda create -n pydicom__pydicom__1.3 python=3.6 numpy -y

SHELL ["conda", "run", "-n", "pydicom__pydicom__1.3", "/bin/bash", "-c"]


RUN pip install pytest

RUN pip install -e .
ENV TESTBED_NAME=pydicom__pydicom__1.3

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]