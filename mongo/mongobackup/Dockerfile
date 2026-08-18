FROM mongo:8.3.8

RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    rm -rf /var/lib/apt/lists/*

ADD backup.sh /backup.sh
ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh /backup.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD [""]
