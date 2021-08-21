#!/bin/sh

# Script to handle spanning LAN with pings
# to populate ARP then grep results for
# the IP of a given MAC

SUBNET=$(ip route | grep '\.0/' | awk '{print $1}')
# echo "SUBNET=$SUBNET"

# This may take 4-5 seconds, so we fork and quickly poll.
# If there are useful results we kill fping.
fping -c1 -t250 -q -g "$SUBNET" 2>/dev/null &
FPING_PID=$!

while ! ( ip neighbor show | grep -qi "$1" ) ; do
  sleep 0.1
done

ip neighbor show | grep -i "$1" | awk '{print $1}' | head -n 1

kill $FPING_PID 2>/dev/null >/dev/null

