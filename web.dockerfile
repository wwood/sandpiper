FROM node:16 as build

WORKDIR /app

COPY vue/package*.json ./
RUN npm install \
 && npm install -g @vue/cli-service \
 && rm package*.json

ARG VUE_APP_API_URL="localhost:5000"

COPY vue ./
RUN npm run build

FROM nginxinc/nginx-unprivileged:stable-alpine as website
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx_site /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]
USER nginx
