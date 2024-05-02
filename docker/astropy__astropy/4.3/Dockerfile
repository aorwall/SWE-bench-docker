FROM aorwall/swe-bench-astropy_astropy:latest

RUN git -c advice.detachedHead=false checkout 298ccb478e6bf092953bca67a3d29dc6c35f6752

RUN conda create -n astropy__astropy__4.3 python=3.9  -y

SHELL ["conda", "run", "-n", "astropy__astropy__4.3", "/bin/bash", "-c"]


RUN pip install attrs==23.1.0 exceptiongroup==1.1.3 execnet==2.0.2 hypothesis==6.82.6 iniconfig==2.0.0 numpy==1.25.2 packaging==23.1 pluggy==1.3.0 psutil==5.9.5 pyerfa==2.0.0.3 pytest-arraydiff==0.5.0 pytest-astropy-header==0.2.2 pytest-astropy==0.10.0 pytest-cov==4.1.0 pytest-doctestplus==1.0.0 pytest-filter-subpackage==0.1.2 pytest-mock==3.11.1 pytest-openfiles==0.5.0 pytest-remotedata==0.4.0 pytest-xdist==3.3.1 pytest==7.4.0 PyYAML==6.0.1 setuptools==68.0.0 sortedcontainers==2.4.0 tomli==2.0.1

RUN pip install -e .[test]
ENV TESTBED_NAME=astropy__astropy__4.3

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]