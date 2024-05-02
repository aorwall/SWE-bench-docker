FROM aorwall/swe-bench-sqlfluff_sqlfluff:latest

RUN git -c advice.detachedHead=false checkout a5c4eae4e3e419fe95460c9afd9cf39a35a470c4

RUN conda create -n sqlfluff__sqlfluff__0.8 python=3.9 -y

SHELL ["conda", "run", "-n", "sqlfluff__sqlfluff__0.8", "/bin/bash", "-c"]


COPY docker/sqlfluff__sqlfluff/0.8/requirements.txt .

RUN pip install -r requirements.txt

RUN pip install -e .
RUN if git show a5c4eae4e3e419fe95460c9afd9cf39a35a470c4:requirements.txt > /dev/null 2>&1; then \
        git checkout a5c4eae4e3e419fe95460c9afd9cf39a35a470c4 -- requirements.txt; \
    else \
        rm -f requirements.txt; \
    fi
ENV TESTBED_NAME=sqlfluff__sqlfluff__0.8

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]