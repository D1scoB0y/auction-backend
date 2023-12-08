FROM nginx:1.25.3-alpine

ARG configdir

VOLUME ./$configdir:/etc/nginx/conf.d:ro

RUN rm /etc/nginx/conf.d/default.conf
COPY $configdir/nginx*.conf /etc/nginx/conf.d/default.conf

VOLUME /etc/letsencrypt:/etc/letsencrypt:ro

CMD ["nginx", "-g", "daemon off;"]
