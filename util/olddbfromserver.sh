#!/bin/sh

echo "[$(date -Is -u)] Dumping database"
ssh -t cualbondi.com.ar "su root -c \"sudo -u postgres 'pg_dump -Fc -Z9 -d geocualbondidb > /tmp/dump.pgbkp'\""

echo "[$(date -Is -u)] Getting file"
rsync -v -e ssh cualbondi.com.ar:/tmp/dump.pgbkp /tmp/dump.pgbkp

echo "[$(date -Is -u)] Inserting in database in local host"
sudo -u postgres pg_restore -C -c -Fc -j8 /tmp/dump.pgbkp