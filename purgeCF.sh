#!/bin/sh

CF_ZONE=$1
CF_KEY=$2
CF_EMAIL=$3

# purge all static files

sleep 10 # wait for github push to take effect

curl -X DELETE "https://api.cloudflare.com/client/v4/zones/$CF_ZONE/purge_cache" \
     -H "X-Auth-Email: $CF_EMAIL" \
     -H "X-Auth-Key: $CF_KEY" \
     -H "Content-Type: application/json" \
     --data '{"purge_everything":true}'

# purge html

curl -X DELETE "https://api.cloudflare.com/client/v4/zones/$CF_ZONE/purge_cache" \
     -H "X-Auth-Email: $CF_EMAIL" \
     -H "X-Auth-Key: $CF_KEY" \
     -H "Content-Type: application/json" \
     --data '{"files":["http://suisui.stream/*.html"]}'

