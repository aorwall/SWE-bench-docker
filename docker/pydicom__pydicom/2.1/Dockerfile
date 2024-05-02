FROM aorwall/swe-bench-pydicom_pydicom:latest

RUN git -c advice.detachedHead=false checkout 506ecea8f378dc687d5c504788fc78810a190b7a

RUN conda create -n pydicom__pydicom__2.1 python=3.9 numpy -y

SHELL ["conda", "run", "-n", "pydicom__pydicom__2.1", "/bin/bash", "-c"]


RUN pip install pytest

RUN pip install -e .
ENV TESTBED_NAME=pydicom__pydicom__2.1

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]