FROM aorwall/swe-bench-pydicom_pydicom:latest

RUN git -c advice.detachedHead=false checkout 9d69811e539774f296c2f289839147e741251716

RUN conda create -n pydicom__pydicom__2.0 python=3.8 numpy -y

SHELL ["conda", "run", "-n", "pydicom__pydicom__2.0", "/bin/bash", "-c"]


RUN pip install pytest

RUN pip install -e .
ENV TESTBED_NAME=pydicom__pydicom__2.0

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]