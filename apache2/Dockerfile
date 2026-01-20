FROM httpd:2.4.66 AS base

ARG DEBIAN_FRONTEND=noninteractive

# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get --no-install-recommends --no-install-suggests --yes --quiet install curl libapache2-mod-auth-openidc \
  && apt-get upgrade --yes \
  && apt-get clean \
  && apt-get --yes --quiet autoremove --purge \
  && rm -rf \
  /var/lib/apt/lists/* \
  /tmp/* \
  /var/tmp/* \
  /usr/share/doc/* \
  /usr/share/groff/* \
  /usr/share/info/* \
  /usr/share/linda/* \
  /usr/share/lintian/* \
  /usr/share/locale/* \
  /usr/share/man/*


COPY ./configs/dev-local.conf /usr/local/apache2/conf/extra/dev-local.conf

RUN echo "LoadModule auth_openidc_module /usr/lib/apache2/modules/mod_auth_openidc.so" >> /usr/local/apache2/conf/httpd.conf \
  && sed -i '/LoadModule proxy_module/s/^#//g' /usr/local/apache2/conf/httpd.conf \
  && sed -i '/LoadModule proxy_http_module/s/^#//g' /usr/local/apache2/conf/httpd.conf \
  && sed -i '/LoadModule headers_module/s/^#//g' /usr/local/apache2/conf/httpd.conf \
  && sed -i '/LoadModule rewrite_module/s/^#//g' /usr/local/apache2/conf/httpd.conf \
  && echo "Include /usr/local/apache2/conf/extra/dev-local.conf" >> /usr/local/apache2/conf/httpd.conf

EXPOSE 80

FROM base AS dev

COPY ./configs/dev-local-destination.conf ./configs/dev-local-origin.conf /usr/local/apache2/conf/extra/

RUN echo "Include /usr/local/apache2/conf/extra/dev-local-destination.conf" >> /usr/local/apache2/conf/httpd.conf \
  && echo "Include /usr/local/apache2/conf/extra/dev-local-origin.conf" >> /usr/local/apache2/conf/httpd.conf

FROM base AS devcontainer

COPY ./configs/devcontainer.conf /usr/local/apache2/conf/extra/

RUN echo "Include /usr/local/apache2/conf/extra/devcontainer.conf" >> /usr/local/apache2/conf/httpd.conf
