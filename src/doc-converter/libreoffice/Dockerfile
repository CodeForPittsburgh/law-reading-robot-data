FROM node:lts-bookworm
WORKDIR /code
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update \
  && apt-get -y  install \
    nodejs \
    tidy \
    libreoffice-writer
COPY . .
RUN npm i --omit=dev
ENTRYPOINT ["bash", "convert.bash"]
