#!/bin/bash

# set variables
ENV_PATH="/app/env"
REPO="/app/repo"

PIP="$ENV_PATH/bin/pip"
PYTHON="$ENV_PATH/bin/python"
MANAGE="$PYTHON $REPO/manage.py"

# exit if some command fails
set -ex

# Install base packages
#apt-get update
apt-get -y install nginx postgresql-9.3-postgis-2.1 uwsgi uwsgi-plugin-python python-pip python-dev libffi-dev libssl-dev libpq-dev cmake libqt4-dev memcached
#pip install -U pip virtualenv

# Configure pgsql
echo "local all postgres trust" > /etc/postgresql/9.3/main/pg_hba.conf
echo "host all postgres 127.0.0.1/32 trust" >> /etc/postgresql/9.3/main/pg_hba.conf
service postgresql restart

set +e
su postgres -c "createdb cualbondi"
set -e
su postgres -c "echo 'create extension postgis;' | psql cualbondi"

# Install base app packages
virtualenv $ENV_PATH
$PIP install -U -r $REPO/requirements.txt

$MANAGE syncdb --all
$MANAGE migrate --fake
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
module = django.core.handlers.wsgi:WSGIHandler()
chdir = /app/repo
pythonpath = /app/repo
socket = /run/uwsgi/app/django/socket
logto = /var/log/uwsgi/django.log
plugins = python
harakiri = 25

spooler-processes = 2
spooler = /var/uwsgi-spooler-django
import = task
HEREDOC

mkdir -p /var/uwsgi-spooler-django
chown www-data. /var/uwsgi-spooler-django

service uwsgi restart
service nginx restart