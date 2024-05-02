FROM aorwall/swe-bench-django_django:latest

RUN git -c advice.detachedHead=false checkout 4a72da71001f154ea60906a2f74898d32b7322a7

RUN conda create -n django__django__5.0 python=3.11 -y

SHELL ["conda", "run", "-n", "django__django__5.0", "/bin/bash", "-c"]


COPY docker/django__django/5.0/requirements.txt .

RUN pip install -r requirements.txt

RUN python -m pip install -e .
RUN if git show 4a72da71001f154ea60906a2f74898d32b7322a7:requirements.txt > /dev/null 2>&1; then \
        git checkout 4a72da71001f154ea60906a2f74898d32b7322a7 -- requirements.txt; \
    else \
        rm -f requirements.txt; \
    fi
ENV TESTBED_NAME=django__django__5.0

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]