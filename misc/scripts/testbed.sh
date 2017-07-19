#!/bin/bash

# Copyright 2016 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

GOVC=govc
CURL=curl
SSH="ssh -q -kTax -o StrictHostKeyChecking=no"

ROOT=root

DEFAULT_TMPDIR="/tmp"
TEST_VM_OVA="test-vm.ova"
TEST_VM1="vdvstest-master"
TEST_VM2="vdvstest-worker1"
TEST_VM3="vdvstest-worker2"

VMS=($TEST_VM1 $TEST_VM2 $TEST_VM3)
TEST_VMS=()
TEST_VM_IPS=()

DOCKER_INFO="docker info"
DOCKERD_PORT=2377

fetch_ova()
{
	tmp=$DEFAULT_TMPDIR
	if [ -n $TEST_TMPDIR]; then
		tmp=$TEST_TMPDIR
	fi

	ova_fpath=$tmp/$TEST_VM_OVA
	$CURL --anyauth -#L $TEST_OVAURL -o $ova_fpath
}

# Delete all test VMs
delete_vms()
{
	for n in ${TEST_VMS[@]}; do
		$GOVC vm.destroy $n
	done
}

# Deploy the test worker VMs to the ESX host and power on 
# the VMs.
deploy_vms()
{
	for n in ${VMS[@]}; do
		vmname=$TEST_USER-$n
		$GOVC vm.ip $vmname > /dev/null 2>&1
		if [ $? -eq 0 ]; then
			TEST_VMS+=($vmname)
			testbed_exists=1
			continue
		fi
		$GOVC import.ova -ds=$TEST_VMDATASTORE -name=$vmname $1
		if [ $? -ne 0 ]; then
			delete_vms
			echo "Failed to deploy VM $vmname"
			exit 1
		fi
		# add the VM to the list of test VMs
		TEST_VMS+=($vmname)
		$GOVC vm.power on=true $vmname
		if [ $? -ne 0 ]; then
			delete_vms
			echo "Failed to power on vm $vmname"
			exit 1
		fi
	done
}

# Get the IPs for each VM deployed earlier
get_vm_ips()
{
	for n in ${TEST_VMS[@]}; do
		vm_ip=`$GOVC vm.ip -a $vmname|cut -f1 -d,`
		# add to the VM IPs list	
		TEST_VM_IPS+=(vm_ip)
	done
}

# Verify if docker is available on the VMs
verify_docker_isrunning()
{
	for vm_ip in ${TEST_VM_IPS[@]}; do
		retry=10
		info=1
		while [ $info -ne 0 ] && [ $retry -gt 0 ]; do
			$SSH $ROOT@vm_ip $DOCKER_INFO
			info=$?
			if [ $info -ne 0 ]; then
				sleep 2
			fi
			retry=`expr $retry - 1`
		done
		if [ $info -ne 0]; then
			echo "Failed to detect docker instance on $vm_ip, deleting setup."
			delete_vms
			exit 1
		fi
	done
}

# Create a docker swarm with one master and two worker nodes
create_docker_swarm()
{
	echo "Creating docker swarm on ${TEST_VMS[@]}"
	master_ip=${TEST_VM_IPS[0]}
	$SSH $ROOT@$master_ip docker node ls > /dev/null 2>&1
	if [ $? -ne 0 ]; then
		$SSH $ROOT@master_ip docker swarm init --advertise-addr $master_ip > /dev/null 2>&1
	fi

	worker_token=`docker swarm join-token -q worker`

	# join the worker nodes to the swarm
	echo "Joining ${TEST_VM_IPS[1]} to the swarm."
	$SSH $ROOT@${TEST_VM_IPS[1]} docker swarm join --token $worker_token $master_ip:$DOCKERD_PORT
	echo "Joining ${TEST_VM_IPS[2]} to the swarm."
	$SSH $ROOT@${TEST_VM_IPS[2]} docker swarm join --token $worker_token $master_ip:$DOCKERD_PORT
}

# Create a manifest of the VMS created
create_manifest()
{

}

if [ $1 -eq 0 ]; then
	for n in ${VMS[@]}; do
		vmname=$TEST_USER-$n
		TEST_VMS+=($vmname)
	done
	delete_vms
	echo "Removed testbed ${TEST_VMS[@]}"
	exit 0
fi

testbed_exists=0
# If an OVA_PATH has been provided then use that to deploy the VMs
# else if an OVA_URL is provided then download the OVA and use that instead
if [ -n $TEST_OVAURL ]; then
	fetch_ova $TEST_OVAURL
	deploy_vms ova_fpath
elif [ -f $TEST_OVAPATH ]; then
	deploy_vms $TEST_OVAPATH
else
	echo "OVA_PATH/OVA_URL not set, no OVA to deploy."
	exit 1
fi

if  [ $testbed_exists -ne 0 ]; then
	echo "Unable to create a new testbed, a testbed is already available - [${TEST_VMS[@]}]"
fi

get_vm_ips

verify_docker_isrunning

create_docker_swarm

create_manifest

#End
