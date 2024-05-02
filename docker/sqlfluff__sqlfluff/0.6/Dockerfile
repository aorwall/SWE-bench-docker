FROM aorwall/swe-bench-sqlfluff_sqlfluff:latest

RUN git -c advice.detachedHead=false checkout 67023b85c41d23d6c6d69812a41b207c4f8a9331

RUN conda create -n sqlfluff__sqlfluff__0.6 python=3.9 -y

SHELL ["conda", "run", "-n", "sqlfluff__sqlfluff__0.6", "/bin/bash", "-c"]


COPY docker/sqlfluff__sqlfluff/0.6/requirements.txt .

RUN pip install -r requirements.txt

RUN pip install -e .
RUN if git show 67023b85c41d23d6c6d69812a41b207c4f8a9331:requirements.txt > /dev/null 2>&1; then \
        git checkout 67023b85c41d23d6c6d69812a41b207c4f8a9331 -- requirements.txt; \
    else \
        rm -f requirements.txt; \
    fi
ENV TESTBED_NAME=sqlfluff__sqlfluff__0.6

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]