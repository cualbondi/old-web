#!/bin/sh

set -e

if [ -z "$1" ]
then
  echo "I need a user as first argument"
  exit 1
fi

log() {
  echo "[$(date -Is -u)] $1"
}

log "Dumping database"
log "I will ask you first password for $1@cualbondi.com.ar, then you'll have to enter password for root@cualbondi.com.ar"
ssh -t $1@cualbondi.com.ar "su root -c \"sudo -u postgres pg_dump -Fc -Z9 -d geocualbondidb > /tmp/dump.pgbkp\""

log "Getting file"
log "I'll need again password for $1@cualbondi.com.ar (hopefully last time to enter password :) )"
rsync -vP -e ssh $1@cualbondi.com.ar:/tmp/dump.pgbkp /tmp/dump.pgbkp

log "Deleting database in local host"
sudo -u postgres dropdb geocualbondidb

log "Inserting in database in local host"
sudo -u postgres pg_restore -C -Fc -j8 /tmp/dump.pgbkp | sudo -u postgresl psql

log "If there was only two error, there is no problem, it all went ok"
log "DONE"