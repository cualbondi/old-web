# Cualbondi

[![shippable status](https://img.shields.io/shippable/56265e141895ca44741ed3a6/master.svg "shippable status")](https://app.shippable.com/projects/56265e141895ca44741ed3a6)
[![wercker status](https://app.wercker.com/status/6e4c78c81a92f06e92b971d476378f14/s/master "wercker status")](https://app.wercker.com/project/bykey/6e4c78c81a92f06e92b971d476378f14)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/695d8e00ab444a4584ceb9b70c39ce63/badge.svg)](https://www.quantifiedcode.com/app/project/695d8e00ab444a4584ceb9b70c39ce63)

[![branch coverage](http://cbcov.bitballoon.com/coverage-branch.svg)](http://cbcov.bitballoon.com/)
[![line coverage](http://cbcov.bitballoon.com/coverage-lines.svg)](http://cbcov.bitballoon.com/)


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
