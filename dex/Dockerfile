FROM dexidp/dex:v2.42.1

COPY ./config.dev.yaml /config.yaml

EXPOSE 5556 5556
EXPOSE 80 80

CMD ["dex", "serve", "/config.yaml"]
