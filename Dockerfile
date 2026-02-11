FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/app/virtualenv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# System deps: Apache + mod_wsgi + Python + mediainfo
RUN apt-get update && apt-get install -y --no-install-recommends \
      apache2 \
      libapache2-mod-wsgi-py3 \
      python3 \
      python3-venv \
      python3-pip \
      ca-certificates \
      mediainfo \
    && rm -rf /var/lib/apt/lists/*

# Apache modules you had before
RUN a2enmod proxy proxy_http proxy_http2 rewrite headers

# Create venv
RUN python3 -m venv "$VIRTUAL_ENV" \
    && pip install --no-cache-dir -U pip setuptools wheel

RUN mkdir /app/pylibs
WORKDIR /app/pylibs

# Copy app
COPY . /app/pylibs 

# Install Python deps first (better layer cache)
RUN pip install --no-cache-dir -r requirements.txt

COPY apache.conf /etc/apache2/sites-available/fixtures.conf

RUN a2dissite "*" && a2ensite fixtures

# Permissions: prefer ownership over 777
RUN mkdir -p /app/www-data \
    && chown -R www-data:www-data /app

# If files.json exists, ensure readable by www-data (not world-writable)
RUN if [ -f "files.json" ]; then chmod 664 files.json; fi

# Send Apache logs to container stdout/stderr
RUN ln -sf /dev/stdout /var/log/apache2/access.log \
 && ln -sf /dev/stderr /var/log/apache2/error.log

EXPOSE 80

# Default Debian Apache foreground command
CMD ["apachectl", "-D", "FOREGROUND"]