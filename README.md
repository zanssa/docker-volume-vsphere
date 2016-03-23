[![Build Status](https://ci.vmware.run/api/badges/vmware/docker-vmdk-plugin/status.svg)](https://ci.vmware.run/vmware/docker-vmdk-plugin)

# Quicksteps to get going

In order to get going, you need to build the plugin, configure test environment
and deploy the plugin to this environment. 
- A simplest way to build is to use
docker - see "Build using docker (Recommended)" section below
- For test, you need ESX and one (or two) Guest Linux VMs inside the ESX. Check out Contributing.md for details on test environment
- once you are done, you can deploy and test using the following:

```
# Build - Requires docker installed.
make
# Deploy - requires test bed prepared
ESX_IP=10.20.105.54 VM_IP=10.20.105.121 make deploy-esx depoy-vm

# Docker commands to use plugin
docker volume create --driver=vmdk --name=MyVolume -o size=10gb
docker volume ls
docker volume inspect MyVolume
docker run --name=my_container -it -v MyVolume:/mnt/myvol -w /mnt/myvol busybox sh
docker volume rm MyVolume # SHOULD FAIL - still used by container
docker rm my_container
docker volume rm MyVolume # Should pass

# To run on ESX manually ("make deploy-esx" does it automatically)
python -B /usr/lib/vmware/vmdkops/bin/vmci_srv.py

# To run on Linux guest manually ("make deploy-vm" does it automatically)
sudo /usr/local/bin/docker-vmdk-plugin

```

To read more about code development and testing read [CONTRIBUTING.md](https://github.com/vmware/docker-vmdk-plugin/blob/master/CONTRIBUTING.md)

# Docker VMDK volume plugin

Native ESXi VMDK support for Docker Data Volumes.

When Docker runs in a VM under ESXi hypervisor, we allow Docker user to
create and use VMDK-based data volumes. Example:

```Shell
docker volume create --driver=vmdk --name=MyStorage -o size=10gb
docker run --rm -it -v MyStorage:/mnt/data busybox sh
```

This will create a MyStorage.vmdk on the same datastore where Docker VM is
located. This vmdk will be attached to the Docker VM on "docker run" and
the containers can use this storage for data.

This repo contains guest code and ESXi code.

The docker-vmdk-plugin service runs in docker VM and talks to Docker Volume
Plugin API via Unix Sockets. It then relays requests via VMWare vSockets
host-guest communication to a dedicated service on ESXi.

The docker plugin code makes use of  vmdkops module  (found  in ./vmdkops)
and ESX python service (found in ./vmdkops-esxsrc).

The end results is that "docker volume create --drive vmdk" is capable
of creating VMDK disks on enclosing ESX host, and using the new volume auto
attaches and mounts the storage so it is immediately usable

## To build:

Build prerequisites:
 - Linux with Docker (1.8+ is supported)
 - git
 - make

Build results are in ./bin.

### Build using docker (Recommended)

Use it when you do not have GO, vibauthor and 32 bit C libraries on your machine,
or do not plan to impact your GO projects.

```Shell
git clone https://github.com/vmware/docker-vmdk-plugin.git
cd docker-vmdk-plugin
make # Build and run unit tests.
make clean
```

There are also the following targets:
```
make clean       # removes binaries build by 'make'
make test        # runs whatever unit tests we have
make deploy      # deploys to your test box (see CONTRIBUTING.md)
make clean-esx   # uninstalls from esx
make clean-vm    # uninstalls from vm
make testremote  # runs sanity check docker commands for volumes
```
Note that `make testremote` reads log output from the plugin at `/var/log/docker-vmdk-plugin.log`.

For more details refer to [CONTRIBUTING.md](https://github.com/vmware/docker-vmdk-plugin/blob/master/CONTRIBUTING.md)

### Build on Photon TP2 Minimal

Photon TP2 Minimal does not have git or make installed, and does not
not start docker by default, so you need to do this before running make:

```Shell
 # Photon TP2 Minimal only:
tyum install -y git
tyum install -y make
systemctl start docker
```
and then the git/cd/make sequence.

### Build without Docker

This build requires
- GO to be installed
- vibauthor
- 32 bit libc headers (as it is needed for ESX-side vSocket shim compilation.)

With these prerequisites, you can do the following to build:

```
mkdir -p $(GOPATH)/src/github.com/vmware
cd $(GOPATH)/src/github.com/vmware
git clone https://github.com/vmware/docker-vmdk-plugin.git
cd docker-vmdk-plugin
make build
```

# WIP
To be continued...
