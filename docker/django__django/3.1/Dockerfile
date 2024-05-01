FROM aorwall/swe-bench-django_django:latest

RUN git -c advice.detachedHead=false checkout 0668164b4ac93a5be79f5b87fae83c657124d9ab



RUN conda create -n django__django__3.1 python=3.6 -y

SHELL ["conda", "run", "-n", "django__django__3.1", "/bin/bash", "-c"]


COPY docker/django__django/3.1/requirements.txt .



RUN pip install -r requirements.txt

RUN python -m pip install -e .


ENV TESTBED_NAME=django__django__3.1

WORKDIR /home/swe-bench

ENTRYPOINT ["./entrypoint.sh"]