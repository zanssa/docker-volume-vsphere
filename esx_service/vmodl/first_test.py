#!/usr/bin/env python
# Copyright 2016 VMWare, Inc. All Rights Reserved.
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

#
# An example of Connecting to (local) VSAN SIMS and fetching simple data 
# from VSAN and VsanDockerPersistentVolumeSystem
#
# Usage: 
#
# 1. drop VsanDockerPersistentVolumeSystem*py files to 
#        /lib/python2.7/site-packages/pyMo/vim/vsan or 
#       /lib64/python3.5/site-packages/pyMo/vim/vsan
#   Do not forget /etc/init.d/vsanmgmtd restart
# 
# 1a. drop the file below (fist_test.py) in local folder or wherever import works from 
#
# 2. in python , run the following:
# import fist_test
# stub = fist_test.connect_to_vsanmgmt()
# fist_test.get_vsan_network_info(stub) # prints vsan info 
# fist_test.get_dockvol_obj(stub)       # prints tenant list (fake string)

import sys
sys.path.append('/lib64/python3.5/site-packages/pyMo/vim/vsan')
sys.path.append('/lib/python2.7/site-packages/pyMo/vim/vsan')

import pyVim
import pyVim.connect
import  pyVim.host

import pyVmomi
import pyVmomi.VmomiSupport
from pyVmomi import vim

from vsanPerfPyMo import VsanPerformanceManager

si = None

def connect_to_vsanmgmt(host = "localhost", port = 443):

    """
    Connects to VSAN mgmt service on ESX (/vsan) and returns SOAP stub
    to use
    """

    version = 'vim.version.version10'

    global si
    if si:
        pyVim.connect.Disconnect(si)

    si = pyVim.connect.Connect(host=host, version=version)
    hostSystem = pyVim.host.GetHostSystem(si)

    token = hostSystem.configManager.vsanSystem.FetchVsanSharedSecret()

    version = pyVmomi.VmomiSupport.newestVersions.Get("vim")
    stub = pyVmomi.SoapStubAdapter(host=host,
                                    port=443,
                                    version=version,
                                    path="/vsan",
                                    poolSize=0)
    vpm = vim.cluster.VsanPerformanceManager("vsan-performance-manager", stub)
    logged_in = vpm.Login(token)

    if not logged_in:
        print("Failed to get sims stub for host %s" % host.name)
        raise OSError("can't login'")

    print("Connected to VSAN mgmt on " + host)
    return stub

def get_vsan_network_info(stub):
    vhs = vim.HostVsanHealthSystem('ha-vsan-health-system', stub)
    return vhs.VsanHostQueryVerifyNetworkSettings()


def get_dockvol_obj(stub):
    import VsanDockerPersistentVolumeSystem
    pv = vim.host.VsanDockerPersistentVolumeSystem("vsan-docker-persistent-volumes", stub)
    return pv.GetTenantList()


if __name__ == "__main__":
    stub = connect_to_vsanmgmt()
    print("\n**** Getting VSAN network info: \n", get_vsan_network_info(stub))

    print("\n**** Getting DOCKVOL TENANTS:")
    tenantsList = get_dockvol_obj(stub)
    print("  total: ", len(tenantsList.tenants),
          "list: ", tenantsList.tenants, 
          "First tenant: ", tenantsList.tenants[0]
    )