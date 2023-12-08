FROM nginx:1.25.3-alpine

ARG configdir

VOLUME ./$configdir:/etc/nginx/conf.d:ro

CMD ["nginx", "-g", "daemon off;"]
