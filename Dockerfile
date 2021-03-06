FROM srittau/wsgi-base:latest

RUN apt-get -y install mediainfo
WORKDIR /app/pylibs
COPY requirements.txt ./
RUN /app/virtualenv/bin/pip install  -r requirements.txt
RUN mkdir /app/www-data
RUN a2enmod proxy proxy_http proxy_http2 rewrite headers
RUN chmod 777 . 

COPY . .
RUN if test -f "files.json"; then chmod 777 files.json; fi

RUN ln -sf /dev/stdout /var/log/apache2/access.log && ln -sf /dev/stderr /var/log/apache2/error.log
