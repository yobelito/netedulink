#!/bin/bash

echo "Verificando la base de datos SSL de Squid..."

# Asegurar que la base de datos SSL está inicializada
if [ ! -d "/var/lib/squid/ssl_db" ]; then
    echo "Inicializando la base de datos SSL para Squid..."
    /usr/local/squid/libexec/security_file_certgen -c -s /var/lib/squid/ssl_db -M 4MB
    chown -R nobody:nogroup /var/lib/squid/ssl_db
    chmod -R 700 /var/lib/squid/ssl_db
fi

echo "Verificando y creando directorios de caché de Squid..."
/usr/local/squid/sbin/squid -z

echo "Eliminando archivos PID previos si existen..."
rm -f /usr/local/squid/var/run/squid.pid

echo "Iniciando Squid..."
exec /usr/local/squid/sbin/squid -N -d 1
