Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/trusty64"

  config.vm.network "forwarded_port", guest: 80, host: 8080

  config.vm.provision "shell", inline: "mkdir -p /app"
  config.vm.synced_folder ".", "/app/repo"
  config.vm.provision "shell", path: "provision.sh"

  config.vm.provider :virtualbox do |vb, override|
    vb.customize ["modifyvm", :id, "--memory", "1024"]
    override.vm.network "private_network", ip: "192.168.2.100"
  end

  config.vm.provider :lxc do |lxc, override|
    lxc.customize 'cgroup.memory.limit_in_bytes', '2048M'
    override.vm.box = "fgrehm/trusty64-lxc"
    override.vm.network "private_network", ip: "192.168.2.100", lxc__bridge_name: 'vlxcbrcb'
  end

end