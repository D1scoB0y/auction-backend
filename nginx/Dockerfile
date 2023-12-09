FROM nginx:1.25.3-alpine

ARG configdir

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

RUN rm /etc/nginx/conf.d/default.conf
COPY $configdir/default.conf /etc/nginx/conf.d/default.conf

COPY monitoring.conf /etc/nginx/conf.d/monitoring.conf

CMD ["nginx", "-g", "daemon off;"]
