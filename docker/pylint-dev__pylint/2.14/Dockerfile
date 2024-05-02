FROM aorwall/swe-bench-pylint-dev_pylint:latest

RUN git -c advice.detachedHead=false checkout 680edebc686cad664bbed934a490aeafa775f163

RUN conda create -n pylint-dev__pylint__2.14 python=3.9 -y

SHELL ["conda", "run", "-n", "pylint-dev__pylint__2.14", "/bin/bash", "-c"]


COPY docker/pylint-dev__pylint/2.14/requirements.txt .

RUN pip install -r requirements.txt

RUN pip install pytest

RUN pip install -e .
RUN if git show 680edebc686cad664bbed934a490aeafa775f163:requirements.txt > /dev/null 2>&1; then \
        git checkout 680edebc686cad664bbed934a490aeafa775f163 -- requirements.txt; \
    else \
        rm -f requirements.txt; \
    fi
ENV TESTBED_NAME=pylint-dev__pylint__2.14

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]