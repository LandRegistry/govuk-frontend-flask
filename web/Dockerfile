FROM node:jod-alpine AS builder

WORKDIR /web

COPY .browserslistrc babel.config.json eslint.config.mjs package*.json webpack.config.js ./
COPY src src

RUN npm install && \
    npm run build

FROM nginx:stable-alpine

RUN apk update && apk add --no-cache openssl && \
    mkdir /etc/nginx/ssl && \
    openssl req -x509 -noenc -newkey rsa:2048 -keyout /etc/nginx/ssl/key.pem -out /etc/nginx/ssl/req.pem -days 90 -subj "/C=GB/ST=Devon/L=Plymouth/O=HM Land Registry/OU=Digital/CN=localhost"

COPY nginx.conf /etc/nginx/conf.d

COPY --from=builder /web/dist /web/static