ARG ROOT_CONTAINER=python:3.7.2-slim

FROM $ROOT_CONTAINER

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install wheel

RUN mkdir /src
ARG CACHE5=24
COPY alkh /src/alkh
COPY README.md /src/
COPY setup.py /src/
WORKDIR /src/
RUN python setup.py sdist bdist_wheel
RUN pip install ./dist/alkh-0.1.4.3-py3-none-any.whl

ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

RUN mkdir /app
RUN mkdir /app/tests
COPY tests/* /app/tests/
WORKDIR /app/
RUN python /app/tests/dump_data_test.py
CMD python /app/tests/analyze_test.py

#RUN pip install prometheus-client==0.12.0
#RUN pip install Jinja2==2.11.3
#RUN pip install prompt-toolkit==2.0.10
#RUN pip install jupyterlab==2.3.2
#CMD ["jupyter-lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]

