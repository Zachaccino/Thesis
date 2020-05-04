FROM alpine

EXPOSE 80

ADD config/default.conf /etc/nginx/conf.d/default.conf

COPY . /var/www/localhost/htdocs

RUN apk add nginx && \
    mkdir /run/nginx && \
    apk add nodejs && \
    apk add npm && \
    cd /var/www/localhost/htdocs && \
    npm install && \
    npm run build && \
    apk del nodejs && \
    apk del npm && \
    mv /var/www/localhost/htdocs/build /var/www/localhost && \
    cd /var/www/localhost/htdocs && \
    rm -rf * && \
    mv /var/www/localhost/build /var/www/localhost/htdocs;


CMD ["/bin/sh", "-c", "exec nginx -g 'daemon off;';"]

WORKDIR /var/www/localhost/htdocs
