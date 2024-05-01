FROM aorwall/swe-bench-django__django:latest

RUN conda create -n django__django__4.0 python=3.8 -y

SHELL ["conda", "run", "-n", "django__django__4.0", "/bin/bash", "-c"]

RUN git -c advice.detachedHead=false checkout 475cffd1d64c690cdad16ede4d5e81985738ceb4


COPY docker/django__django/4.0/requirements.txt .



RUN pip install -r requirements.txt

RUN python -m pip install -e .


ENV TESTBED_NAME=django__django__4.0

WORKDIR /home/swe-bench

ENTRYPOINT ["./entrypoint.sh"]