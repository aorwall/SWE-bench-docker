FROM aorwall/swe-bench-pydicom_pydicom:latest

RUN git -c advice.detachedHead=false checkout a8be738418dee0a2b93c241fbd5e0bc82f4b8680

RUN conda create -n pydicom__pydicom__2.3 python=3.10 numpy -y

SHELL ["conda", "run", "-n", "pydicom__pydicom__2.3", "/bin/bash", "-c"]


RUN pip install pytest

RUN pip install -e .
ENV TESTBED_NAME=pydicom__pydicom__2.3

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]