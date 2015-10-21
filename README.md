# Cualbondi

[![shippable status](https://img.shields.io/shippable/56265e141895ca44741ed3a6/master.svg "shippable status")](https://app.shippable.com/projects/56265e141895ca44741ed3a6)
[![wercker status](https://app.wercker.com/status/6e4c78c81a92f06e92b971d476378f14/s/master "wercker status")](https://app.wercker.com/project/bykey/6e4c78c81a92f06e92b971d476378f14)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/695d8e00ab444a4584ceb9b70c39ce63/badge.svg)](https://www.quantifiedcode.com/app/project/695d8e00ab444a4584ceb9b70c39ce63)

## Requirements

* Debian-based machine
* Maybe macos? Does lxc work there? If not, lxc can be changed to work with virtualbox easily.

## Dev install

    # vagrant vagrant-lxc installation
    sudo apt-get install dpkg-dev
    wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.2_x86_64.deb
    dpkg -i vagrant_1.7.2_x86_64.deb
    
    vagrant plugin install vagrant-lxc
    
    # cualbondi code setup and launch app
    git clone git@bitbucket.org:martinzugnoni/geocualbondi.git
    # git clone https://<username>@bitbucket.org/martinzugnoni/geocualbondi.git # HTTPS alternative
    
    vagrant up
    # vagrant up --provider=lxc  # alternative
    
Now you can go to localhost:8000 or 192.168.2.100:80 in the browser and enjoy cualbondi.

### Internal working

All this works inside vagrant machine

1. Vagrant mounts the directory in which the Vagrantfile is located outside vagrant machine (git root), inside the vagrant virtual machine to be accesed as `/repo`.

2. Inside vagrant machine, uwsgi uses `/app/repo` to work, and communicates to nginx through a unix socket located in `/run/uwsgi/app/django/socket`

3. Inside vagrant machine, NginX acts as a reverse proxy for uwsgi, exposing application into port 80

4. Vagrant NATs port 80 inside vm to 8000 outside in localhost and creates a bridged network with ip 192.168.2.100 to communicate directly with the host

### Developing workflow

Change files in repo outside vagrant machine.

Then do `vagrant ssh -c 'sudo service uwsgi restart'`.

To make uwsgi to autoreload django app on `*.py` files modifications, enter the vagrant machine and uncomment line hich says `py-autoreload=2`

Do F5 in localhost:8000

To use `manage.py`, enter vagrant machine doing `vagrant ssh` and execute `manage.py` like this `/app/env/bin/python /app/repo/manage.py`

## Database cloning

You can download a copy of production database running `vagrant ssh -c 'source /app/repo/pulldb.sh <user>'` (`<user>` being a linux user from cualbondi main server)

## Production install

The same as dev install can be done, but changing the settings.py
