# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  config.vm.box = "bento/ubuntu-16.04"

  config.vm.network "forwarded_port", guest: 8000, host: 8000  # Use guest's NGINX proxy
  config.vm.network "forwarded_port", guest: 8001, host: 8001
  config.vm.network "forwarded_port", guest: 8080, host: 8080

  config.vm.synced_folder "~/workspaces/public/geonode.git", "/home/vagrant/geonode"
  #config.vm.synced_folder "~/workspaces/public/geodash-framework-django.git", "/home/vagrant/geodash-framework-django.git"
  #config.vm.synced_folder "~/workspaces/public/geodash-plugin-geonode-dashboards.git", "/home/vagrant/geodash-plugin-geonode-dashboards.git"
  #config.vm.synced_folder "~/workspaces/public/geodash-plugin-navbars.git", "/home/vagrant/geodash-plugin-navbars.git"
  #config.vm.synced_folder "~/workspaces/public/geodash.js.git", "/home/vagrant/geodash.js.git"
  #config.vm.synced_folder "~/workspaces/public/geodash-base.git", "/home/vagrant/geodash-base.git"

  config.vm.provider "virtualbox" do |vb|\
      vb.gui = false
      vb.cpus = 2
      vb.memory = 4096
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/ubuntu_geonode.yml"
    ansible.host_key_checking = false
    ansible.verbose = "v"
    ansible.raw_arguments = []
  end

end
