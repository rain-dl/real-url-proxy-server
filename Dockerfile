FROM --platform=$BUILDPLATFORM node:alpine as base

RUN apk add --no-cache python3 python3-dev py3-pip
RUN pip3 install requests PyExecJS

FROM base as build

ENV PORT 8888
ENV REFRESH 7200

COPY . /real-url-proxy-server
WORKDIR /real-url-proxy-server

ENTRYPOINT python3 real-url-proxy-server.py --port $PORT --refresh $REFRESH
