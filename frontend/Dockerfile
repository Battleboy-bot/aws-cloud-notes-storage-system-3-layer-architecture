FROM nginx:1.27-alpine

ENV API_BASE_URL=https://xxxxxxxx.execute-api.ap-south-1.amazonaws.com/api/v1 \
    NGINX_ENVSUBST_OUTPUT_DIR=/usr/share/nginx/html/static/js

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY static /usr/share/nginx/html/static
COPY static/js/config.js.template /etc/nginx/templates/config.js.template

EXPOSE 80
