FROM alpine

RUN apk add --no-cache \
    bash \
    git \
    github-cli

COPY entrypoint.py /entrypoint.py

RUN chmod +x /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]