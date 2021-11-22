FROM alpine

ENV PYTHONUNBUFFERED=1

RUN apk add --update --no-cache \
    bash \
#    git \
#    github-cli \
    python3

COPY entrypoint.py /entrypoint.py

RUN chmod +x /entrypoint.py

CMD ["/entrypoint.py"]
ENTRYPOINT ["python3"]