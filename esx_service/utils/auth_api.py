import auth
import auth_data_const
import convert
import auth_data
import vmdk_utils

def get_auth_mgr():
    try:
        auth_mgr = auth.get_auth_mgr()
    except auth_data.DbConnectionError, e:
        error_info = "Failed to connect auth DB({0})".format(e)
        return error_info, None
    return None, auth_mgr

def get_tenant_from_db(name):
    error_info, auth_mgr = get_auth_mgr()
    if error_info:
        return error_info, None

    error_info, tenant = auth_mgr.get_tenant(name)
    return error_info, tenant

def create_tenant_in_db(name, description, default_datastore, default_privileges, vms, privileges):
    error_info, auth_mgr = get_auth_mgr()
    if error_info:
        return error_info, None

    error_info, tenant = auth_mgr.create_tenant(name = name, 
                                                description = description, 
                                                default_datastore = default_datastore, 
                                                default_privileges = default_privileges, 
                                                vms = vms, 
                                                privileges = privileges)
    return error_info, tenant

def get_tenant_list_from_db():
    error_info, auth_mgr = get_auth_mgr()
    if error_info:
        return error_info, None
    
    error_info, tenant_list = auth_mgr.list_tenants()
    return error_info, tenant_list

def generate_tuple_from_vm_list(vm_list):
    """ Generate a list of (vm_uuid, vm_name) pair """
    if not vm_list:
        return None, []
    vms = []
    for vm_name in vm_list:
        vm_uuid = vmdk_utils.get_vm_uuid_by_name(vm_name)
        if not vm_uuid:
            error_info =  "Cannot find vm_uuid for vm {0}, tenant_create failed".format(vm_name)
            return error_info, None
        vms.append((vm_uuid, vm_name))
    
    return None, vms

def default_privileges():
     privileges = [{'datastore': 'datastore1',
                     'global_visibility': 0,
                      'create_volume': 0,
                      'delete_volume': 0,
                     'mount_volume': 0,
                      'max_volume_size': 0,
                      'usage_quota': 0}]
     return privileges

def set_privileges(rights, privileges, value):
    """ set or unset privileges based rights passed by command line """
    if 'create' in rights:
        privileges[auth_data_const.COL_CREATE_VOLUME] = value

    if 'delete' in rights:
        privileges[auth_data_const.COL_DELETE_VOLUME] = value

    if 'mount' in rights:
        privileges[auth_data_const.COL_MOUNT_VOLUME] = value

    if 'all' in rights:
        privileges[auth_data_const.COL_CREATE_VOLUME] = value
        privileges[auth_data_const.COL_DELETE_VOLUME] = value
        privileges[auth_data_const.COL_MOUNT_VOLUME] = value

def generate_privileges(datastore, rights, volume_maxsize, volume_totalsize):
    """ Generate privileges based on CLI argument """
    privileges = default_privileges()[0]
    privileges[auth_data_const.COL_DATASTORE] = datastore
    
    if rights:
        set_privileges(rights, privileges, 1)
    
    if volume_maxsize:
        size_in_MB = convert.convert_to_MB(volume_maxsize)
        privileges[auth_data_const.COL_MAX_VOLUME_SIZE] = size_in_MB
    
    if volume_totalsize:
        size_in_MB = convert.convert_to_MB(volume_totalsize)
        privileges[auth_data_const.COL_USAGE_QUOTA] = size_in_MB
    
    return privileges

def modify_privileges(privileges, add_rights, rm_rights, volume_maxsize, volume_totalsize):
    """ Modify privileges based on CLI argument """
    if add_rights:
        set_privileges(add_rights, privileges, 1)
        
    if rm_rights:
        set_privileges(rm_rights, privileges, 0)

    if volume_maxsize:
        size_in_MB = convert.convert_to_MB(volume_maxsize)
        privileges[auth_data_const.COL_MAX_VOLUME_SIZE] = size_in_MB
    
    if volume_totalsize:
        size_in_MB = convert.convert_to_MB(volume_totalsize)
        privileges[auth_data_const.COL_USAGE_QUOTA] = size_in_MB
    
    return privileges

def generate_privileges_dict(privileges):
    # privileges is a list which is read from auth DB
    # it has the following format
    # (tenant_uuid, datastore, global_visibility, create_volume, delete_volume,
    # mount_volume, max_volume_size, usage_quota)
    privileges_dict = {}
    privileges_dict[auth_data_const.COL_DATASTORE] = privileges[1]
    privileges_dict[auth_data_const.COL_GLOBAL_VISIBILITY] = privileges[2]
    privileges_dict[auth_data_const.COL_CREATE_VOLUME] = privileges[3]
    privileges_dict[auth_data_const.COL_DELETE_VOLUME] = privileges[4]
    privileges_dict[auth_data_const.COL_MOUNT_VOLUME] = privileges[5]
    privileges_dict[auth_data_const.COL_MAX_VOLUME_SIZE] = privileges[6]
    privileges_dict[auth_data_const.COL_USAGE_QUOTA] = privileges[7]
    return privileges_dict

def _tenant_create(name, description, default_datastore, default_privileges, vm_list, privileges):
    """ API to create a tenant """
    error_info, vms = generate_tuple_from_vm_list(vm_list)
    if error_info:
        return error_info, None
    
    error_info, tenant = create_tenant_in_db(
                                             name = name, 
                                             description = description, 
                                             default_datastore = default_datastore, 
                                             default_privileges = default_privileges, 
                                             vms = vms, 
                                             privileges = privileges)
    if error_info:
        return error_info, None
    
    return None, tenant


def _tenant_rm(name, remove_volumes):
    """ API to remove a tenant """
    error_info, tenant = get_tenant_from_db(name)
    if error_info:
        return error_info
    
    error_info, auth_mgr = get_auth_mgr()
    if error_info:
        return error_info

    error_info = auth_mgr.remove_tenant(tenant.id, remove_volumes)
    return error_info

def _tenant_ls():
    error_info, tenant_list = get_tenant_list_from_db()
    return error_info, tenant_list

def _tenant_vm_add(name, vm_list):
    """ API to add vms for a tenant """
    error_info, tenant = get_tenant_from_db(name)
    if error_info:
        return error_info
    
    if not tenant:
        error_info = "Tenant {0} does not exist".format(name)
        return error_info

    error_info, vms = generate_tuple_from_vm_list(vm_list)
    if error_info:
        return error_info
    
    error_info, auth_mgr = get_auth_mgr()
    if error_info:
        return error_info
 
    error_info = tenant.add_vms(auth_mgr.conn, vms)
    return error_info

def _tenant_vm_rm(name, vm_list):
    """ API to remove vms for a tenant """
    error_info, tenant = get_tenant_from_db(name)
    if error_info:
        return error_info
    
    if not tenant:
        error_info = "Tenant {0} does not exist".format(name)
        return error_info

    error_info, vms = generate_tuple_from_vm_list(vm_list)
    
    if error_info:
        return error_info
    
    error_info, auth_mgr = get_auth_mgr()
    if error_info:
        return error_info
      
    error_info = tenant.remove_vms(auth_mgr.conn, vms)
    return error_info


def _tenant_vm_ls(name):
    """ API to get vms for a tenant """
    error_info, tenant = get_tenant_from_db(name)
    if error_info:
        return error_info, None
    
    if not tenant:
        error_info = "Tenant {0} does not exist".format(name)
        return error_info, None
   
    return None, tenant.vms

def _tenant_access_add(name, datastore, rights, volume_maxsize, volume_totalsize):
    """ API to add datastore access for a tenant """
    error_info, tenant = get_tenant_from_db(name)
    if error_info:
        return error_info

    if not tenant:
        error_info = "Tenant {0} does not exist".format(name)
        return error_info

    privileges = generate_privileges(datastore, rights, volume_maxsize, volume_totalsize)
    
    error_info, auth_mgr = get_auth_mgr()
    if error_info:
        return error_info

    error_info = tenant.set_datastore_access_privileges(auth_mgr.conn, [privileges])
    return error_info

def _tenant_access_set(name, datastore, add_rights, rm_rights, volume_maxsize, volume_totalsize):
    """ API to modify datastore access for a tenant """
    error_info, tenant = get_tenant_from_db(name)
    if error_info:
        return error_info

    if not tenant:
        error_info = "Tenant {0} does not exist".format(name)
        return error_info

    privileges = [d for d in tenant.privileges if d[auth_data_const.COL_DATASTORE] == datastore]
    
    if not privileges:
        error_info = "No privileges exist for ({0}, {1})".format(name, datastore)
        return error_info
    
    privileges_dict = generate_privileges_dict(privileges[0])
    privileges_dict = modify_privileges(privileges_dict, add_rights, rm_rights, volume_maxsize, volume_totalsize)

    error_info, auth_mgr = get_auth_mgr()
    if error_info:
        return error_info

    error_info = tenant.set_datastore_access_privileges(auth_mgr.conn, [privileges_dict])
    return error_info

def _tenant_access_rm(name, datastore):
    """ API to remove datastore access for a tenant """
    error_info, tenant = get_tenant_from_db(name)
    if error_info:
        return error_info
    
    error_info, auth_mgr = get_auth_mgr()
    if error_info:
        return error_info

    error_info = tenant.remove_datastore_access_privileges(auth_mgr.conn, datastore)
    return error_info

def _tenant_access_ls(name):
    """ Handle tenant access ls command """
    error_info, tenant = get_tenant_from_db(name)
    if error_info:
        return error_info, None

    return None, tenant.privileges 
    
    
      
    

