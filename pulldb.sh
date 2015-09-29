#!/bin/sh

set -e

if [ -z "$1" ]
then
  echo "I need a user as first argument"
  exit 1
fi

echo "[$(date -Is -u)] Dumping database"
echo "I will ask you first password for $1@cualbondi.com.ar, then you'll have to enter password for root@cualbondi.com.ar"
ssh -t $1@cualbondi.com.ar "su root -c \"sudo -u postgres pg_dump -Fc -Z9 -d geocualbondidb > /tmp/dump.pgbkp\""

echo "[$(date -Is -u)] Getting file"
echo "I'll need again password for $1@cualbondi.com.ar (hopefully last time to enter password :) )"
rsync -vP -e ssh $1@cualbondi.com.ar:/tmp/dump.pgbkp /tmp/dump.pgbkp

echo "[$(date -Is -u)] Inserting in database in local host"
sudo -u postgres pg_restore -d postgres -C -c -Fc -j8 /tmp/dump.pgbkp

echo "[$(date -Is -u)] If there was only two error, there is no problem, it all went ok"
echo "[$(date -Is -u)] DONE"