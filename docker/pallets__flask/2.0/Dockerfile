FROM aorwall/swe-bench-pallets_flask:latest

RUN git -c advice.detachedHead=false checkout 4346498c85848c53843b810537b83a8f6124c9d3

RUN conda create -n pallets__flask__2.0 python=3.9 -y

SHELL ["conda", "run", "-n", "pallets__flask__2.0", "/bin/bash", "-c"]


COPY docker/pallets__flask/2.0/requirements.txt .

RUN pip install -r requirements.txt

RUN pip install Werkzeug==2.3.7 Jinja2==3.0.1 itsdangerous==2.1.2 click==8.0.1 MarkupSafe==2.1.3

RUN pip install -e .
RUN if git show 4346498c85848c53843b810537b83a8f6124c9d3:requirements.txt > /dev/null 2>&1; then \
        git checkout 4346498c85848c53843b810537b83a8f6124c9d3 -- requirements.txt; \
    else \
        rm -f requirements.txt; \
    fi
ENV TESTBED_NAME=pallets__flask__2.0

WORKDIR /home/swe-bench

COPY swebench swebench
COPY docker/entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]