#!/bin/sh

echo "[$(date -Is -u)] Dumping database"
ssh -t cualbondi.com.ar "su root -c \"sudo -u postgres pg_dump -Fc -f /tmp/dump.pgbkp geocualbondidb\""

echo "[$(date -Is -u)] Getting file"
rsync -v -e ssh cualbondi.com.ar:/tmp/dump.pgbkp /tmp/dump.pgbkp

echo "[$(date -Is -u)] Inserting in database in local host"
sudo -u postgres pg_restore /tmp/dump.pgbkp