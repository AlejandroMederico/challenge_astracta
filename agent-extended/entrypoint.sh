#!/bin/sh

set -e
if [ -n "$OPENID_URL" ]; then
  SERVER="${OPENID_URL##http://}"
  SERVER="${SERVER%%/*}"
  ./wait-for-it.sh -t 60 "${SERVER}"
fi

exec "$@"