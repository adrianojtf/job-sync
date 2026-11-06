# Imagem do frontend job-sync: build com Node e arquivos estáticos servidos pelo Nginx.

FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Vazio: a UI chama a API na mesma origem e o Nginx encaminha /v1 para o backend.
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
# Endereço do backend visto de dentro do container (ex.: serviço "backend" do docker compose).
ENV API_UPSTREAM=http://backend:8000
EXPOSE 80
