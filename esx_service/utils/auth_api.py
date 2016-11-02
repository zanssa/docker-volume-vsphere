import auth
import auth_data_const
import convert
import auth_data


def _tenant_create(name, description, default_datastore, default_privileges, vms, privileges):
    """ Handle tenant create command """
    error_info, tenant = create_tenant_in_db(
                                             name = name, 
                                             description = description, 
                                             default_datastore = default_datastore, 
                                             default_privileges = default_privileges, 
                                             vms = vms, 
                                             privileges = privileges)
    return error_info, tenant


def _tenant_rm(name, remove_volumes):
    """ Handle tenant rm command """
    error_info, tenant = get_tenant_from_db(args.name)
    if error_info:
        return error_info 
    
    error_info = _auth_mgr.remove_tenant(tenant.id, remove_volumes)
    if error_info:
        return error_info
