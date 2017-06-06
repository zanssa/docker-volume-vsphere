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

// A home to hold test constants related with vmdkops_admin cli.

package admincli

const (
	// PolicyName is the name of vsan policy which will be used in test
	PolicyName = "some-policy"

	// PolicyContent is the content of vsan policy which will be used in test
	PolicyContent = "'((\"proportionalCapacity\" i50)''(\"hostFailuresToTolerate\" i0))'"

	// vsanDatastore is the name of vsanDatastore which will be used in test
	vsanDatastore = "vsanDatastore"

	// VsanVol1 is the name of volume to be created on vsanDatastore
	VsanVol1 = "vsanVol1@" + vsanDatastore
)
