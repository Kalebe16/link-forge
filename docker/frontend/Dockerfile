FROM node:24-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY frontend/package*.json ./

RUN npm ci

COPY frontend .

RUN npm run build

RUN npm install -g serve

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "5173"]
