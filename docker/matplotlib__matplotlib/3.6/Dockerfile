FROM aorwall/swe-bench-matplotlib_matplotlib:latest

RUN git -c advice.detachedHead=false checkout 73909bcb408886a22e2b84581d6b9e6d9907c813

COPY docker/matplotlib__matplotlib/3.6/environment.yml .
RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "matplotlib__matplotlib__3.6", "/bin/bash", "-c"]


RUN pip install contourpy==1.1.0 cycler==0.11.0 fonttools==4.42.1 kiwisolver==1.4.5 numpy==1.25.2 packaging==23.1 pillow==10.0.0 pyparsing==3.0.9 python-dateutil==2.8.2 six==1.16.0 setuptools==68.1.2 setuptools-scm==7.1.0 typing-extensions==4.7.1

RUN python -m pip install -e .
RUN if git show 73909bcb408886a22e2b84581d6b9e6d9907c813:environment.yml > /dev/null 2>&1; then \
        git checkout 73909bcb408886a22e2b84581d6b9e6d9907c813 -- environment.yml; \
    else \
        rm -f requirements.txt; \
    fi
ENV TESTBED_NAME=matplotlib__matplotlib__3.6

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]