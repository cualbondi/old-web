#!/bin/bash
# Instalacion de todo lo necesario para el server

#solo root puede ejecutar el script
if [ $(id -u) -eq 0 ]; then

    #apt-get update
    apt-get install git python-django python-psycopg2 python-memcache postgresql postgis postgresql-9.1-postgis proj-bin gdal-bin python-django-piston python-pip libapache2-mod-wsgi
    pip install django-moderation django-floppyforms

    # Instalacion de la base de datos bajo el $USER
    DB_USER=geocualbondiuser
    DB_NAME=geocualbondidb
    DB_PASS=geocualbondipass
    su postgres -c "createuser -RSD $DB_USER"
    su postgres -c "createdb $DB_NAME"
    su postgres -c "psql -d $DB_NAME -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql"
    su postgres -c "psql -d $DB_NAME -f /usr/share/postgresql/9.1/contrib/postgis_comments.sql"
    su postgres -c "psql -d $DB_NAME -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql"

    su postgres -c "psql -d $DB_NAME -c \"alter user $DB_USER with password '$DB_PASS';\""
    su postgres -c "psql -d $DB_NAME -c \"grant select on spatial_ref_sys to $DB_USER;\""
    su postgres -c "psql -d $DB_NAME -c \"grant select,update,insert,delete on geometry_columns to $DB_USER;\""

    # useradd o adduser
    # Script to add a user to Linux system http://www.cyberciti.biz/tips/howto-write-shell-script-to-add-user.html
    SYS_USER=cualbondi
    SYS_PASS=facebook,puto
    adduser --gecos $SYS_USER $SYS_USER --disabled-password
    echo "$SYS_USER:$SYS_PASS" | chpasswd

    # git clone
    HOMEDIR=/home/$SYS_USER/geocualbondi
    GIT_URL=https://jperelli@bitbucket.org/martinzugnoni/geocualbondi.git
    cd /home/$SYS_USER
    su $SYS_USER -c "git clone $GIT_URL" ||
    (cd $HOMEDIR && su $SYS_USER -c "git pull")
# por ssh tira el siguiente error...
#  Warning: Permanently added 'bitbucket.org,207.223.240.181' (RSA) to the list of known hosts.
#  Permission denied (publickey).
# la clave del https es 123210

    # django manage.py conf user y crear tablas
    perl -pi -e "s|'NAME': '.*?',|'NAME': '$DB_NAME',|" $HOMEDIR/settings.py
    perl -pi -e "s|'USER': '.*?',|'USER': '$DB_USER',|" $HOMEDIR/settings.py
    perl -pi -e "s|'PASSWORD': '.*?',|'PASSWORD': '$DB_PASS',|" $HOMEDIR/settings.py
    python $HOMEDIR/manage.py syncdb
    
    # apache conf wsgi
    (cat <<EOF
    <VirtualHost *:80>

	ServerName localhost
	DocumentRoot $HOMEDIR

	<Directory $HOMEDIR >
		Order allow,deny
		Allow from all
	</Directory>

	WSGIDaemonProcess geocualbondi.djangoserver processes=2 threads=15 display-name=%{GROUP}
	WSGIProcessGroup geocualbondi.djangoserver

    Alias /robots.txt $HOMEDIR/static/robots.txt
    Alias /favicon.ico $HOMEDIR/static/favicon.ico

    AliasMatch ^/([^/]*\\.css) $HOMEDIR/static/styles/\$1

    Alias /media/ $HOMEDIR/media/
    Alias /static/ $HOMEDIR/static/

    <Directory $HOMEDIR/media>
    Order deny,allow
    Allow from all
    </Directory>

    <Directory $HOMEDIR/media>
    Order deny,allow
    Allow from all
    </Directory>

    WSGIScriptAlias / $HOMEDIR/wsgi.py

    ErrorLog \${APACHE_LOG_DIR}/dj-error.log

    </VirtualHost>
EOF
) > /etc/apache2/sites-available/django

    sed -i "1,/sys.path.append/ {/sys.path.append/i sys.path.append('$HOMEDIR/')\nsys.path.append('/home/$SYS_USER/')
}" $HOMEDIR/wsgi.py

    perl -pi -e "s|\"DJANGO_SETTINGS_MODULE\", \".*?\"|\"DJANGO_SETTINGS_MODULE\", \"geocualbondi.settings\"|" $HOMEDIR/wsgi.py


    ## opcional osm script
    ## opcional provincias script
    ## opcional add features script

    ## Para habilitar phppgadmin con user postgres pass postgres: http://localhost/phppgadmin/
    ## TODO: prompt y/n, and pass
    #apt-get install phppgadmin
    #echo -e "postgres:postgres" | chpasswd
    #su postgres -c "psql -c \"alter user postgres with password 'postgres';\""
    #sed -i "s/conf['extra_login_security'] = true/conf['extra_login_security'] = false/g" /etc/phppgadmin/config.inc.php

    # reparar error de geodjango+postgresql
    perl -pi -e "s|#?standard_conforming_strings = on|standard_conforming_strings = off|" /etc/postgresql/9.1/main/postgresql.conf
    /etc/init.d/postgresql restart

    a2ensite django
    apache2ctl restart

else
    echo "ERROR: debe ejecutar el script como root"
    exit 2
fi
