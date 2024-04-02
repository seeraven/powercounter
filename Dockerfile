ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

ADD . /powercounter
WORKDIR /powercounter

RUN make system-setup-prod

WORKDIR /powercounter/src
ENTRYPOINT [ "/powercounter/src/docker_entrypoint.sh" ]
# ENTRYPOINT [ "/usr/local/bin/python3", "/powercounter/src/powercounter"]
