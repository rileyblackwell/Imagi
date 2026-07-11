#!/bin/sh
# Generate an nginx resolver config from the container's DNS settings.
# Required because nginx.conf uses a variable in proxy_pass, which makes
# nginx re-resolve backend.railway.internal per request instead of caching
# the IP at startup (Railway assigns a new private IP on every redeploy).
set -e

ns=$(awk '/^nameserver/ {print $2; exit}' /etc/resolv.conf)

# Bracket IPv6 addresses for nginx (Railway's private DNS is IPv6)
case "$ns" in
  *:*) ns="[$ns]" ;;
esac

echo "resolver $ns valid=10s;" > /etc/nginx/conf.d/00-resolver.conf
echo "10-set-resolver.sh: using resolver $ns"
