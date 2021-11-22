FROM alpine

RUN apk add --no-cache \
    bash \
    git \
    github-cli

COPY entrypoint.py /entrypoint.sh

RUN chmod +x /entrypoint.py

ENTRYPOINT ["/entrypoint.sh"]