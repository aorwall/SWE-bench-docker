FROM aorwall/swe-bench-sympy_sympy:latest

RUN git -c advice.detachedHead=false checkout 70381f282f2d9d039da860e391fe51649df2779d

RUN conda create -n sympy__sympy__1.5 python=3.9 mpmath flake8 -y

SHELL ["conda", "run", "-n", "sympy__sympy__1.5", "/bin/bash", "-c"]


RUN pip install mpmath==1.3.0 flake8-comprehensions

RUN pip install -e .
ENV TESTBED_NAME=sympy__sympy__1.5

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]