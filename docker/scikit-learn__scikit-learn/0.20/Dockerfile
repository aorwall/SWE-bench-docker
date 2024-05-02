FROM aorwall/swe-bench-scikit-learn_scikit-learn:latest

RUN git -c advice.detachedHead=false checkout 55bf5d93e5674f13a1134d93a11fd0cd11aabcd1

RUN conda create -n scikit-learn__scikit-learn__0.20 python=3.6 numpy scipy cython pytest pandas matplotlib -y

SHELL ["conda", "run", "-n", "scikit-learn__scikit-learn__0.20", "/bin/bash", "-c"]


RUN pip install numpy==1.19.2 scipy==1.5.2

RUN pip install -v --no-use-pep517 --no-build-isolation -e .
ENV TESTBED_NAME=scikit-learn__scikit-learn__0.20

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]