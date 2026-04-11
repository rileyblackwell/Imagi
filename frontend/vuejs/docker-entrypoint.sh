#!/bin/sh
# Extract the first nameserver from /etc/resolv.conf so nginx can resolve
# *.railway.internal at runtime. Railway injects its own DNS into resolv.conf,
# and only that DNS knows the private network hostnames (public resolvers
# like 8.8.8.8 return NXDOMAIN).
set -eu
DNS_RESOLVER=$(awk '/^nameserver/ { print $2; exit }' /etc/resolv.conf)
DNS_RESOLVER=${DNS_RESOLVER:-8.8.8.8}
sed -i "s|RAILWAY_DNS_RESOLVER|${DNS_RESOLVER}|g" /etc/nginx/conf.d/default.conf
echo "[entrypoint] nginx resolver set to ${DNS_RESOLVER}"
exec nginx -g 'daemon off;'
