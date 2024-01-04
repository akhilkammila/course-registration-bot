#!/bin/sh
# wait for backend using netcat (nc)

set -e

host="$1"
shift
cmd="$@"

until nc -z "$host" 5000; do
  >&2 echo "Backend is unavailable - sleeping"
  sleep 1
done

>&2 echo "Backend is up - executing command"
exec $cmd