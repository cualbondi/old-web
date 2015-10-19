#!/bin/bash

# set variables
ENV_PATH="/app/env"
REPO="/app/repo"

PIP="$ENV_PATH/bin/pip"
PYTHON="$ENV_PATH/bin/python"
MANAGE="$PYTHON $REPO/manage.py"
DB_NAME="geocualbondidb"

# exit if some command fails
set -ex


# TODO: use postgresl 9.4 official repo http://apt.postgresql.org/pub/repos/apt/ utopic-pgdg/main amd64 Packages
# Install base packages
apt-get update
apt-get -y install nginx postgresql-9.3-postgis-2.1 postgresql-client uwsgi uwsgi-plugin-python python-pip python-dev libffi-dev libssl-dev libpq-dev cmake libqt4-dev memcached osm2pgsql rsync libgeos-dev gdal-bin libjpeg-dev zlib1g-dev git pngcrush
pip install -U pip virtualenv

# Configure pgsql
echo "local all postgres trust" > /etc/postgresql/9.3/main/pg_hba.conf
echo "host all postgres 127.0.0.1/32 trust" >> /etc/postgresql/9.3/main/pg_hba.conf
service postgresql restart

set +e
su postgres -c "createdb $DB_NAME"
set -e
su postgres -c "echo 'create extension postgis;' | psql $DB_NAME"
su postgres -c "echo 'create extension pg_trgm;' | psql $DB_NAME"
su postgres <<-HEREDOC1
    psql -d $DB_NAME <<-HEREDOC2
    
    CREATE OR REPLACE FUNCTION
        min_linestring ( "line1" Geometry, "line2" Geometry )
        RETURNS geometry
        AS \\\$$
        BEGIN
            IF ST_Length2D_Spheroid(line1, 'SPHEROID["GRS_1980",6378137,298.257222101]') < ST_Length2D_Spheroid(line2, 'SPHEROID["GRS_1980",6378137,298.257222101]') THEN
                RETURN line1;
            ELSE
                RETURN line2;
            END IF;
        END;
        \\\$$ LANGUAGE plpgsql;
        
    CREATE AGGREGATE min_path ( Geometry ) (
        SFUNC = min_linestring,
        STYPE = Geometry);

HEREDOC2
HEREDOC1


# Install base app packages
virtualenv $ENV_PATH
$PIP install -U -r $REPO/requirements.txt

$MANAGE migrate --noinput
$MANAGE collectstatic --noinput

cat > /etc/nginx/sites-enabled/default <<HEREDOC
server {
        server_name _;
        listen   80;

        location /media {
                alias /app/media/;
                location ~*  \.(jpg|jpeg|png|gif|ico|css|js)$ {
                         expires 5d;
                }
        }

        location /static {
                alias /app/static/;
                location ~*  \.(jpg|jpeg|png|gif|ico|css|js|woff|eot|svg)$ {
                         expires 5d;
                }
        }

        location /robots.txt {
        #        alias /app/static/robots-disallow-all.txt;
                alias /app/static/robots.txt;
        }

        location /favicon.ico {
                alias /app/static/img/favicon.png;
        }

        access_log  /var/log/nginx/app_access.log;
        error_log   /var/log/nginx/app_error.log;

        location / {
                uwsgi_read_timeout 30s;
                uwsgi_send_timeout 30s;
                uwsgi_pass unix:///run/uwsgi/app/django/socket;
                include uwsgi_params;
        }
}
HEREDOC



cat > /etc/uwsgi/apps-enabled/django.ini <<HEREDOC
[uwsgi]
virtualenv = /app/env
threads = 3
workers = 4
master = true
env = DJANGO_SETTINGS_MODULE=settings
#env = CUALBONDI_ENV=production
module = django.core.wsgi:get_wsgi_application()
chdir = /app/repo
pythonpath = /app/repo
socket = /run/uwsgi/app/django/socket
logto = /var/log/uwsgi/django.log
plugins = python
harakiri = 25

# for development only
# py-autoreload=2

spooler-processes = 2
spooler = /var/uwsgi-spooler-django
import = task
HEREDOC

mkdir -p /var/uwsgi-spooler-django
chown www-data. /var/uwsgi-spooler-django

service uwsgi restart
service nginx restart
