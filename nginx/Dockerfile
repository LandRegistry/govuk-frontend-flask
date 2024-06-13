FROM nginx:stable

RUN rm /etc/nginx/conf.d/default.conf && \
  mkdir /etc/nginx/ssl && \
  openssl req -x509 -noenc -newkey rsa:2048 -keyout /etc/nginx/ssl/key.pem -out /etc/nginx/ssl/req.pem -days 90 -subj "/C=GB/ST=Devon/L=Plymouth/O=HM Land Registry/OU=DDaT/CN=localhost" && \
  openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

COPY nginx.conf /etc/nginx/conf.d