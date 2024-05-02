FROM aorwall/swe-bench-django_django:latest

RUN git -c advice.detachedHead=false checkout 65dfb06a1ab56c238cc80f5e1c31f61210c4577d

RUN conda create -n django__django__3.2 python=3.6 -y

SHELL ["conda", "run", "-n", "django__django__3.2", "/bin/bash", "-c"]


COPY docker/django__django/3.2/requirements.txt .

RUN pip install -r requirements.txt

RUN python -m pip install -e .
RUN if git show 65dfb06a1ab56c238cc80f5e1c31f61210c4577d:requirements.txt > /dev/null 2>&1; then \
        git checkout 65dfb06a1ab56c238cc80f5e1c31f61210c4577d -- requirements.txt; \
    else \
        rm -f requirements.txt; \
    fi
ENV TESTBED_NAME=django__django__3.2

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]