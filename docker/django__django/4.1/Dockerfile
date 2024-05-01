FROM aorwall/swe-bench-django_django:latest

RUN git -c advice.detachedHead=false checkout 647480166bfe7532e8c471fef0146e3a17e6c0c9



RUN conda create -n django__django__4.1 python=3.9 -y

SHELL ["conda", "run", "-n", "django__django__4.1", "/bin/bash", "-c"]


COPY docker/django__django/4.1/requirements.txt .



RUN pip install -r requirements.txt

RUN python -m pip install -e .


ENV TESTBED_NAME=django__django__4.1

WORKDIR /home/swe-bench

ENTRYPOINT ["./entrypoint.sh"]