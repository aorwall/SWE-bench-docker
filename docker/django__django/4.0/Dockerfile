FROM aorwall/swe-bench-django_django:latest

RUN git -c advice.detachedHead=false checkout 475cffd1d64c690cdad16ede4d5e81985738ceb4

RUN conda create -n django__django__4.0 python=3.8 -y

SHELL ["conda", "run", "-n", "django__django__4.0", "/bin/bash", "-c"]


COPY docker/django__django/4.0/requirements.txt .

RUN pip install -r requirements.txt

RUN python -m pip install -e .
RUN if git show 475cffd1d64c690cdad16ede4d5e81985738ceb4:requirements.txt > /dev/null 2>&1; then \
        git checkout 475cffd1d64c690cdad16ede4d5e81985738ceb4 -- requirements.txt; \
    else \
        rm -f requirements.txt; \
    fi
ENV TESTBED_NAME=django__django__4.0

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]