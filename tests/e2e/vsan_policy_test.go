// Copyright 2017 VMware, Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// This test suite tries to vsan policy related tests

package e2e

import (
	"log"

	adminclicon "github.com/vmware/docker-volume-vsphere/tests/constants/admincli"
	"github.com/vmware/docker-volume-vsphere/tests/utils/admincli"
	"github.com/vmware/docker-volume-vsphere/tests/utils/dockercli"
	"github.com/vmware/docker-volume-vsphere/tests/utils/govc"
	"github.com/vmware/docker-volume-vsphere/tests/utils/inputparams"
	"github.com/vmware/docker-volume-vsphere/tests/utils/misc"
	"github.com/vmware/docker-volume-vsphere/tests/utils/verification"
	. "gopkg.in/check.v1"
)

type VsanPolicyTestSuite struct {
	config *inputparams.TestConfig
	esxIP  string
	hostIP string
}

func (s *VsanPolicyTestSuite) SetUpSuite(c *C) {
	s.config = inputparams.GetTestConfig()
	if s.config == nil {
		c.Skip("Unable to retrieve test config, skipping vsan_policy tests")
	}
	admincli.ConfigInit(s.config.EsxHost)
	s.esxIP = s.config.EsxHost
	s.hostIP = s.config.DockerHosts[0]
	log.Printf("SetupSuite: esxIP[%s] hostIP[%s]\n", s.esxIP, s.hostIP)
}

func (s *VsanPolicyTestSuite) TearDownSuite(c *C) {
	out, err := admincli.ConfigRemove(s.esxIP)
	c.Assert(err, IsNil, Commentf(out))
}

var _ = Suite(&VsanPolicyTestSuite{})

var (

	// vsanDatastore is the name of vsanDatastore which will be used in test
	vsanDatastore = govc.GetDatastoreByType("vsan")

	// VsanVol1 is the name of volume to be created on vsanDatastore
	VsanVol1 = inputparams.GetVolumeNameWithTimeStamp("vsan_policy_test") + "@" + vsanDatastore
)

// Test step:
// 1. create a vsan policy
// 2. run "vmdkops_admin policy ls", check the "Active" column of the output to make sure it
// is shown as "Unused"
// 3. create a volume on vsanDatastore with the vsan policy we created
// 4. run "docker volume inspect" on the volume to verify the output "vsan-policy-name" field
// 5. run "vmdkops_admin policy ls", check the "Active" column of the output to make sure it
// is shown as "In use by 1 volumes"
// 6. run "vmdkops_admin policy rm" to remove the policy, which should fail since the volume is still
// use the vsan policy
func (s *VsanPolicyTestSuite) TestDeleteVsanPolicyAlreadyInUse(c *C) {
	misc.LogTestStart("VsanPolicyTestSuite", "TestDeleteVsanPolicyAlreadyInUse")

	out, err := admincli.CreateVsanPolicy(s.esxIP, adminclicon.PolicyName, adminclicon.PolicyContent)
	c.Assert(err, IsNil, Commentf(out))

	res := admincli.VerifyActiveFromVsanPolicyListOutput(s.esxIP, adminclicon.PolicyName, "Unused")
	c.Assert(res, Equals, true, Commentf("vsanPolicy should be \"Unused\""))

	out, err = dockercli.CreateVolumeWithOptions(s.hostIP, VsanVol1, " -o vsan-policy-name="+adminclicon.PolicyName)
	c.Assert(err, IsNil, Commentf(out))

	policyName := verification.GetPolicyNameForVol(VsanVol1, s.hostIP)
	c.Assert(policyName, Equals, adminclicon.PolicyName, Commentf("The name of vsan policy used by volume "+VsanVol1+" returns incorrect value "+policyName))

	res = admincli.VerifyActiveFromVsanPolicyListOutput(s.esxIP, adminclicon.PolicyName, "In use by 1 volumes")
	c.Assert(res, Equals, true, Commentf("vsanPolicy should be \"In use by 1 volumes\""))

	out, err = admincli.RemoveVsanPolicy(s.esxIP, adminclicon.PolicyName)
	log.Printf("Remove vsanPolicy \"%s\" returns with %s", adminclicon.PolicyName, out)
	c.Assert(out, Matches, "Error: Cannot remove.*", Commentf("vsanPolicy is still used by volumes and cannot be removed"))

	misc.LogTestEnd("VsanPolicyTestSuite", "TestDeleteVsanPolicyAlreadyInUse")

}
