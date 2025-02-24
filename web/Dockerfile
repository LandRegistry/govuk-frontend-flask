FROM node:jod-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

FROM nginx:stable-alpine

RUN apk update && apk add --no-cache openssl && \
    mkdir /etc/nginx/ssl && \
    openssl req -x509 -noenc -newkey rsa:2048 -keyout /etc/nginx/ssl/key.pem -out /etc/nginx/ssl/req.pem -days 90 -subj "/C=GB/ST=Devon/L=Plymouth/O=HM Land Registry/OU=Digital/CN=localhost"

COPY nginx.conf /etc/nginx/conf.d
COPY --from=builder /app/node_modules/govuk-frontend/dist/govuk/assets /app/static/assets/
COPY --from=builder /app/node_modules/govuk-frontend/dist/govuk/govuk-frontend.min.* /app/static