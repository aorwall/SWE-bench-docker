FROM aorwall/swe-bench-django_django:latest

RUN git -c advice.detachedHead=false checkout 419a78300f7cd27611196e1e464d50fd0385ff27



RUN conda create -n django__django__3.0 python=3.6 -y

SHELL ["conda", "run", "-n", "django__django__3.0", "/bin/bash", "-c"]


COPY docker/django__django/3.0/requirements.txt .



RUN pip install -r requirements.txt

RUN python -m pip install -e .


ENV TESTBED_NAME=django__django__3.0

WORKDIR /home/swe-bench

ENTRYPOINT ["./entrypoint.sh"]