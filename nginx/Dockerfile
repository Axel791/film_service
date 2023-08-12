FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/
COPY servers/proxy_params /etc/nginx/
#COPY servers/admin.conf /etc/nginx/servers/
#COPY servers/api.conf /etc/nginx/servers/
#COPY servers/auth.conf /etc/nginx/servers/
COPY servers/kafka.conf /etc/nginx/servers/

