FROM aorwall/swe-bench-matplotlib_matplotlib:latest

RUN git -c advice.detachedHead=false checkout 0849036fd992a2dd133a0cffc3f84f58ccf1840f


COPY docker/matplotlib__matplotlib/3.7/environment.yml .


RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "matplotlib__matplotlib__3.7", "/bin/bash", "-c"]




RUN pip install contourpy==1.1.0 cycler==0.11.0 fonttools==4.42.1 kiwisolver==1.4.5 numpy==1.25.2 packaging==23.1 pillow==10.0.0 pyparsing==3.0.9 python-dateutil==2.8.2 six==1.16.0 setuptools==68.1.2 setuptools-scm==7.1.0 typing-extensions==4.7.1

RUN python -m pip install -e .


ENV TESTBED_NAME=matplotlib__matplotlib__3.7

WORKDIR /home/swe-bench

ENTRYPOINT ["./entrypoint.sh"]