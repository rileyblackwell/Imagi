#!/bin/sh
# Extract the nameserver from /etc/resolv.conf so Nginx can resolve
# Railway private network hostnames (*.railway.internal).
# These are only resolvable by Railway's internal DNS, not public DNS.
DNS_RESOLVER=$(awk '/^nameserver/ { print $2; exit }' /etc/resolv.conf)
DNS_RESOLVER=${DNS_RESOLVER:-8.8.8.8}

sed -i "s/RAILWAY_DNS_RESOLVER/${DNS_RESOLVER}/g" /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
