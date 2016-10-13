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

"""
Copyright 2016 VMware, Inc.  All rights reserved. 
Licensed under the Apache License, Version 2.0 
http://www.apache.org/licenses/LICENSE-2.0
"""

from VmodlDecorators import ManagedType, EnumType, Method, \
   Return, RegisterVmodlTypes, F_OPTIONAL, Param, DataType, Attribute
from pyVmomi import Vmodl
from pyVmomi.VmomiSupport import newestVersions

try:
   from asyncVmodlEmitterLib import JavaDocs, Internal
except ImportError:
   pass
   def JavaDocs(parent, docs):
      def Decorate(f):
         return f
      return Decorate
   def Internal(parent):
      def Decorate(f):
         return f
      return Decorate


# _VERSION = newestVersions.Get("vim")
_VERSION = 'vim.version.version10'

# Vmodl Names

class VsanDockerPersistentVolumeTenantList:
   _name = "vim.vsan.VsanDockerPersistentVolumeTenantList"
   @JavaDocs(parent=_name, docs =
   """
   This class encapsulates the Docker Volume Tenant List Result.
   """
   )
   
   @DataType(name=_name, version=_VERSION)
   def __init__(self):
      pass

   @JavaDocs(parent=_name, docs =
   """
   Defines a list of tenants
   """
   )
   @Attribute(parent=_name, typ="string[]")
   def tenants(self):
      pass


class VsanDockerPersistentVolumeSystem:
   ''' This is the API to Docker Persistent Volumes on VSAN'''

   _name = "vim.host.VsanDockerPersistentVolumeSystem"

   @Internal(parent=_name)
   @ManagedType(name=_name, version=_VERSION)
   def __init__(self):
      pass

   @JavaDocs(parent=_name, docs=
   """
   Query the tenant list. This method returns a list of tenants, as strings. 
   The method is blocking on requires DB IO. 
   It SHOULD be converted to async task, eventually.
   """
   )
   @Method(parent=_name, wsdlName="GetTenantList")
   @Return(typ="vim.vsan.VsanDockerPersistentVolumeTenantList")
   def GetTenantList(self):
      pass


RegisterVmodlTypes()
