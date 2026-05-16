FROM python:3.12-slim

# Install tini for proper signal handling
ENV TINI_VERSION v0.19.0
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
  && apt-get install -y --no-install-recommends wget gnupg2 \
  && wget -qO /usr/local/bin/tini https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-amd64 \
  && chmod +x /usr/local/bin/tini \
  && apt-get purge -y --auto-remove wget gnupg2 \
  && rm -rf /var/lib/apt/lists/*

# Create app user and group
ARG APP_USER=scraper
ARG APP_UID=1001
RUN groupadd -g ${APP_UID} ${APP_USER} \
  && useradd -m -u ${APP_UID} -g ${APP_UID} -s /sbin/nologin ${APP_USER}

WORKDIR /usr/src/app

# Copy only needed files and install deps as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=${APP_USER}:${APP_USER} . .

# Drop to non-root user
USER ${APP_USER}

# Use tini as entrypoint to forward signals; run scraper in foreground
ENTRYPOINT ["/usr/local/bin/tini", "--"]
CMD ["python", "./scraper.py"]