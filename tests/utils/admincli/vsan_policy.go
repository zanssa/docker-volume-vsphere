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

// This util holds various helper methods related to vsan policy to be consumed by testcases.

package admincli

import (
	"log"
	"strings"

	"github.com/vmware/docker-volume-vsphere/tests/constants/admincli"
	"github.com/vmware/docker-volume-vsphere/tests/utils/ssh"
)

// CreateVsanPolicy method is going to create a vsan policy.
func CreateVsanPolicy(ip, policyName, policyContent string) (string, error) {
	log.Printf("Creating a vsanPolicy [%s] on esx [%s]\n", policyName, ip)
	return ssh.InvokeCommand(ip, admincli.CreateVsanPolicy+policyName+" --content="+policyContent)
}

// RemoveVsanPolicy method is going to remove a vsan policy.
func RemoveVsanPolicy(ip, policyName string) (string, error) {
	log.Printf("Removing a vsanPolicy [%s] on esx [%s]\n", policyName, ip)
	return ssh.InvokeCommand(ip, admincli.RemoveVsanPolicy+policyName)
}

// VerifyActiveFromVsanPolicyListOutput is going to check, for the given vsan policy, the active
// column returned by "vmdkops policy ls" command is the same as the value specified by
// param @active
func VerifyActiveFromVsanPolicyListOutput(ip, policyName, active string) bool {
	log.Printf("Verify vsanPolicy [%s] on esx [%s] has active as %s\n", policyName, ip, active)
	cmd := admincli.ListVsanPolicy + " 2>/dev/null | grep " + policyName
	out, err := ssh.InvokeCommand(ip, cmd)
	if err != nil {
		return false
	}
	log.Printf("policy ls output for vsanPolicy [%s] is %s:", policyName, out)
	return strings.Contains(out, active)
}
