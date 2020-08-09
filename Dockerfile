FROM php:7.2-apache
RUN apt update && apt install -y zlib1g-dev && rm -rf /var/lib/apt/lists/*
RUN docker-php-ext-install -j$(nproc) pdo pdo_mysql zip

RUN yes | pecl install xdebug \
    && echo "zend_extension=$(find /usr/local/lib/php/extensions/ -name xdebug.so)" > /usr/local/etc/php/conf.d/xdebug.ini \
    && echo "xdebug.remote_enable=on" >> /usr/local/etc/php/conf.d/xdebug.ini \
    && echo "xdebug.remote_autostart=off" >> /usr/local/etc/php/conf.d/xdebug.ini

COPY . /var/www/html/
RUN date +%s >/var/www/html/version.txt
