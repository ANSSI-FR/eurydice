FROM osixia/openldap:1.5.0

ENV LDAP_TLS=false
ENV LDAP_DOMAIN=eury.test

COPY ./config-ldap.ldif /container/service/slapd/assets/config/bootstrap/ldif/config-ldap.ldif

CMD ["--copy-service"]
