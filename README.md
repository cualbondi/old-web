# Cualbondi

## Requirements

* Debian-based machine
* Maybe macos? Does lxc work there? If not, lxc can be changed to work with virtualbox easily.

## Dev install

    # vagrant vagrant-lxc and fabric installation
    sudo apt-get install dpkg-dev
    wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.2_x86_64.deb
    dpkg -i vagrant_1.7.2_x86_64.deb
    
    vagrant plugin install vagrant-lxc
    
    # cualbondi code setup and launch app
    git clone git@bitbucket.org:martinzugnoni/geocualbondi.git
    # git clone https://<username>@bitbucket.org/martinzugnoni/geocualbondi.git # HTTPS alternative
    
    vagrant up
    # vagrant up --provider=lxc # maybe this alternative
    
Now you can go to localhost:8000 or 192.168.2.100:80 in the browser and enjoy cualbondi.

### Internal working

All this works inside vagrant machine, in this case a lxc container

1. Vagrant mounts the directory in which the Vagrantfile is located outside vagrant machine (git root), inside the vagrant virtual machine to be accesed as `/repo`.

2. Inside vagrant machine, uwsgi uses `/repo` to work and communicates to nginx through a unix socket located in `/run/uwsgi/app/django/socket`

3. Inside vagrant machine, NginX acts as a reverse proxy for uwsgi, exposing application into port 80

4. Vagrant NATs port 80 inside vm to 8000 outside in localhost and creates a bridged network with ip 192.168.2.100 to communicate directly with the host

### Developing workflow

Change files in repo outside vagrant machine.

Then do `vagrant ssh -c 'sudo service uwsgi restart'`.

Do F5 in localhost:8000

This can also be configured to work with runserver. To do that, use `vagrant ssh` to connect to the vagrant machine and run commands inside. Then shutdown nginx with `sudo service nginx stop` and initiate runserver with `sudo /app/env/bin/python /app/repo/manage.py runserver 0.0.0.0:80`

## Database cloning

Database dumps are stored in server daily. They can be downloaded and applied to the local server running `vagrant ssh -c '/app/env/bin/python /app/repo/manage.py copyDBfromserver'`

## Production install

The same as dev install can be done, but changing the settings.py