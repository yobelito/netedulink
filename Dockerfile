FROM ubuntu:20.04

# Instalar dependencias necesarias para compilar Squid con SSL
RUN apt-get update && apt-get install -y \
    build-essential gcc g++ libpcre3 libpcre3-dev zlib1g-dev libssl-dev wget curl unzip perl \
    libdb5.3-dev libexpat1-dev libcap2-dev libldap2-dev libpam0g-dev libcppunit-dev \
    ca-certificates

# Descargar y compilar Squid con soporte para SSL Bump
WORKDIR /usr/local/src
RUN wget http://www.squid-cache.org/Versions/v6/squid-6.10.tar.gz && \
    tar -xzf squid-6.10.tar.gz && cd squid-6.10 && \
    ./configure --prefix=/usr/local/squid \
                --enable-ssl-crtd \
                --enable-ssl \
                --with-openssl && \
    make -j$(nproc) && make install

# Crear directorios y establecer permisos
RUN mkdir -p /var/spool/squid /etc/squid/ssl_cert /var/log/squid /var/lib/squid && \
    chown -R nobody:nogroup /var/spool/squid /etc/squid/ssl_cert /var/log/squid /var/lib/squid && \
    chmod -R 755 /var/spool/squid /var/log/squid /var/lib/squid

# Copiar configuración personalizada de Squid
COPY squid.conf /usr/local/squid/etc/squid.conf

# Copiar script de inicialización dentro del contenedor
COPY init-squid.sh /usr/local/bin/init-squid.sh
RUN chmod +x /usr/local/bin/init-squid.sh

# Exponer puertos
EXPOSE 3128 3129

# Definir el script de inicio como entrypoint
ENTRYPOINT ["/usr/local/bin/init-squid.sh"]
