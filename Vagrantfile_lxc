Vagrant.configure("2") do |config|
  
  config.vm.box = "fgrehm/trusty64-lxc"
  
  config.vm.provision "shell", inline: "mkdir -p /app"
  
  config.vm.synced_folder ".", "/app/repo"
  
  config.vm.provider :lxc do |lxc|
    lxc.customize 'cgroup.memory.limit_in_bytes', '1024M'
  end
  
  config.vm.provision "shell", path: "provision.sh"
  
  config.vm.network "private_network", ip: "192.168.2.100", lxc__bridge_name: 'vlxcbr1'
  config.vm.network "forwarded_port", guest: 80, host: 8080
  
end