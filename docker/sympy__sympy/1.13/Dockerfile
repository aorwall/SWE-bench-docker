FROM aorwall/swe-bench-sympy_sympy:latest

RUN git -c advice.detachedHead=false checkout be161798ecc7278ccf3ffa47259e3b5fde280b7d

RUN conda create -n sympy__sympy__1.13 python=3.9 -y

SHELL ["conda", "run", "-n", "sympy__sympy__1.13", "/bin/bash", "-c"]


COPY docker/sympy__sympy/1.13/requirements.txt .

RUN pip install -r requirements.txt

RUN pip install mpmath==1.3.0

RUN pip install -e .
RUN if git show be161798ecc7278ccf3ffa47259e3b5fde280b7d:requirements.txt > /dev/null 2>&1; then \
        git checkout be161798ecc7278ccf3ffa47259e3b5fde280b7d -- requirements.txt; \
    else \
        rm -f requirements.txt; \
    fi
ENV TESTBED_NAME=sympy__sympy__1.13

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]