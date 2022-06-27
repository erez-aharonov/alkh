#ARG ROOT_CONTAINER=ubuntu:focal
#ARG ROOT_CONTAINER=ubuntu:bionic
ARG ROOT_CONTAINER=python:3.6.0-slim

FROM $ROOT_CONTAINER

RUN mkdir /app
COPY dist/* /app/
RUN pip install --upgrade pip
RUN pip install prometheus-client==0.12.0
RUN pip install Jinja2==2.11.3
RUN pip install prompt-toolkit==2.0.10
RUN pip install /app/alkh-0.1.3-py3-none-any.whl
RUN pip install jupyterlab==2.3.2

ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

RUN mkdir /app/tests
COPY tests/* /app/tests/
RUN python /app/tests/dump_data_test.py
#RUN ls /usr/bin/
RUN which python
RUN pip list


CMD ["jupyter-lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]

