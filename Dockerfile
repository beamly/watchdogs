# Note that this is not currently available as a public image.
# For now, please just build this image locally:
# `docker build . -t watchdogs:latest`

FROM alpine:3.6

COPY requirements.txt /tmp/requirements.txt
RUN apk add --update openssl-dev musl-dev libffi-dev gcc python python-dev py-pip \
  && rm -rf /var/cache/apk/* \
  && pip install -r /tmp/requirements.txt \
  && mkdir -p /app/enabled_tests

COPY available_tests /app/available_tests

WORKDIR /app
ENTRYPOINT ["py.test", "enabled_tests/"]
