# Cualbondi

[![wercker status](https://app.wercker.com/status/d93ca25465dc45adb58b99c01e0662ff/s/master "wercker status")](https://app.wercker.com/project/byKey/d93ca25465dc45adb58b99c01e0662ff)

[![Coverage Status](https://coveralls.io/repos/github/cualbondi/cualbondi.com.ar/badge.svg?branch=master)](https://coveralls.io/github/cualbondi/cualbondi.com.ar?branch=master)

[![Code Climate](https://codeclimate.com/github/cualbondi/cualbondi.com.ar/badges/gpa.svg)](https://codeclimate.com/github/cualbondi/cualbondi.com.ar)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/e36cba74aeca4d3387a0b41c029419bd)](https://www.codacy.com/app/jperelli/cualbondi-com-ar?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=cualbondi/cualbondi.com.ar&amp;utm_campaign=Badge_Grade)

## Requirements

* Ubuntu 16.04 at least to run in vagrant-lxc
* In macos it should work with vagrant+virtualbox

## Dev install

#### 1. Prereqs

    sudo apt-get install vagrant

    # use your fork and then request a pull if you plan to contribute
    git clone git@github.com:cualbondi/cualbondi.com.ar.git

#### 2a. vagrant lxc (ubuntu) (fastest!)

    sudo apt-get install vagrant dpkg-dev zlib1g-dev

    # maybe read this, not always needed https://github.com/rubygems/rubygems/commit/044b0e2685e4b219b013f1067d670918a48c1f62#commitcomment-14935888
    sudo vagrant plugin install vagrant-lxc

    vagrant lxc sudoers # put sudo pass and then
    vagrant up --provider=lxc

If the last command does not work (trying lxc, some error with sudo something) go to

    cd ~/.vagrant.d/gems/gems/
    rm -rf vagrant-lxc-1.2.1
    git clone git@github.com:fgrehm/vagrant-lxc.git vagrant-lxc-1.2.1
    cd -
    # and now try again
    vagrant up --provider=lxc


#### 2b (alternative). vagrant virtualbox (slower, for windows / macos)

    vagrant up

#### ready!

Now you can go to http://192.168.2.100:80/ in the browser and enjoy cualbondi.

To access django's admin interface go to http://192.168.2.100/admin/ and login with user `admin` pass `admin`

### Internal working

All this works inside vagrant machine

1. Vagrant mounts the directory in which the Vagrantfile is located outside vagrant machine (git root), inside the vagrant virtual machine to be accesed as `/repo`.

2. Inside vagrant machine, uwsgi uses `/app/repo` to work, and communicates to nginx through a unix socket located in `/run/uwsgi/app/django/socket`

3. Inside vagrant machine, NginX acts as a reverse proxy for uwsgi, exposing application into port 80

4. Vagrant NATs port 80 inside vm to 8000 outside in localhost and creates a bridged network with ip 192.168.2.100 to communicate directly with the host

### Developing workflow

Change files in repo outside vagrant machine.

Then do `vagrant ssh -c 'sudo service uwsgi restart'` to autoreload all `*.py` files

To make uwsgi to autoreload django app on `*.py` files modifications, enter the vagrant machine and uncomment line which says `py-autoreload=2` in file `/etc/uwsgi/apps-enabled/django.ini`

Do F5 in localhost:8000

To use `manage.py`, enter vagrant machine doing `vagrant ssh` and execute `manage.py` like this `/app/env/bin/python /app/repo/manage.py`

## Database cloning

> This is not open to public, we are working on an alternative to have data to play.
> We want to release all data, but we need to make sure we don't release sensible things like real users emails.

You can download a copy of production database running `vagrant ssh -c 'source /app/repo/pulldb.sh <user>'` (`<user>` being a linux user from cualbondi main server)

## Production install

The same as dev install can be done, but changing the settings.py or adding a settings_local.py which overrides settings

## License

Cualbondi software is distributed under GNU AGPLv3. See LICENSE file on directory root.

## Developers

 - Julian Perelli
 - Martin Zugnoni
