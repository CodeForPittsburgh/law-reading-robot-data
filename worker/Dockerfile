FROM node:lts-bookworm AS builder
WORKDIR /code
COPY . .
RUN npm i
RUN npm run build

FROM builder AS db_builder
CMD [ "npx", "prisma", "migrate", "dev", "--name", "init", "--schema", "./dal/prisma/schema.prisma"]


FROM node:lts-bookworm
WORKDIR /code
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update \
  && apt-get -y  install \
    tidy \
    libreoffice-writer
COPY --from=builder /code/node_modules ./node_modules
COPY --from=builder /code/package*.json ./
COPY --from=builder /code/build ./build

CMD [ "bash", "-c", "sleep infinity" ]
