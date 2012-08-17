import datetime

import keystone.backends.api as db_api
import keystone.backends.models as db_models


def add_user(name, password, tenant=None):
    if tenant:
        tenant = db_api.TENANT.get_by_name(tenant).id

    obj = db_models.User()
    obj.name = name
    obj.password = password
    obj.enabled = True
    obj.tenant_id = tenant
    return db_api.USER.create(obj)


def disable_user(name):
    user = db_api.USER.get_by_name(name)
    if user is None:
        raise IndexError("User %s not found" % name)
    user.enabled = False
    return db_api.USER.update(user.id, user)


def list_users():
    objects = db_api.USER.get_all()
    if objects == None:
        raise IndexError("No users found")
    return [[o.id, o.name, o.enabled, o.tenant_id] for o in objects]

def add_billunit(vcpu, ram, vdisk):
    obj = db_models.BillUnit()
    obj.vcpu = vcpu
    obj.ram = ram
    obj.enabled = True
    obj.vdisk = vdisk
    obj.date = date
    return db_api.BILLER.create(obj)
	
def revoke_billunit():
    objects = db_api.BILLER.get()
    if objects == None:
        raise IndexError("No Biller  found")
    return [[o.id, o.vcpu, o.ram, o.vdisk,o.date] for o in objects]
	
def add_instance_bill(id, name, total_vcpu, total_ram, total_vdisk, changed_on):
    obj = db_models.InstanceBills()
    obj.id=id
    obj.total_vcpu =total_vcpu
    obj.total_ram = total_ram
    obj.enabled = True
    obj.total_vdisk = total_vdisk
    obj.name = name;
    obj.changed_on = changed_on
    return db_api.BILLER.create_instance_bill(obj)

def revoke_instance_bill():
    objects = db_api.BILLER.get_instance_bill()
    if objects == None:
        raise IndexError("No Instance Biller  found")
    return [[o.id, o.name, o.total_vcpu, o.total_ram, o.total_vdisk, o.total_cost, o.changed_on] for o in objects]


def add_tenant(name):
    obj = db_models.Tenant()
    obj.name = name
    obj.enabled = True
    return db_api.TENANT.create(obj)



def list_tenants():
    objects = db_api.TENANT.get_all()
    if objects == None:
        raise IndexError("Tenants not found")
    return [[o.id, o.name, o.enabled] for o in objects]


def disable_tenant(name):
    obj = db_api.TENANT.get_by_name(name)
    if obj == None:
        raise IndexError("Tenant %s not found" % name)
    obj.enabled = False
    return db_api.TENANT.update(obj.id, obj)


def add_role(name):
    obj = db_models.Role()
    obj.name = name
    role = db_api.ROLE.create(obj)
    return role


def list_role_assignments(tenant):
    objects = db_api.TENANT.get_role_assignments(tenant)
    if objects == None:
        raise IndexError("Assignments not found")
    return [[o.user_id, o.role_id] for o in objects]


def list_roles(tenant=None):
    if tenant:
        tenant = db_api.TENANT.get_by_name(tenant).id
        return list_role_assignments(tenant)
    else:
        objects = db_api.ROLE.get_all()
        if objects == None:
            raise IndexError("Roles not found")
        return [[o.id, o.name] for o in objects]


def grant_role(role, user, tenant=None):
    """Grants `role` to `user` (and optionally, on `tenant`)"""
    role = db_api.ROLE.get_by_name(name=role).id
    user = db_api.USER.get_by_name(name=user).id

    if tenant:
        tenant = db_api.TENANT.get_by_name(name=tenant).id

    obj = db_models.UserRoleAssociation()
    obj.role_id = role
    obj.user_id = user
    obj.tenant_id = tenant

    return db_api.USER.user_role_add(obj)


def add_endpoint_template(region, service, public_url, admin_url, internal_url,
    enabled, is_global):
    db_service = db_api.SERVICE.get_by_name(service)
    if db_service is None:
        raise IndexError("Service %s not found" % service)
    obj = db_models.EndpointTemplates()
    obj.region = region
    obj.service_id = db_service.id
    obj.public_url = public_url
    obj.admin_url = admin_url
    obj.internal_url = internal_url
    obj.enabled = enabled
    obj.is_global = is_global
    return db_api.ENDPOINT_TEMPLATE.create(obj)


def list_tenant_endpoints(tenant):
    objects = db_api.ENDPOINT_TEMPLATE.endpoint_get_by_tenant(tenant)
    if objects == None:
        raise IndexError("URLs not found")
    return [[db_api.SERVICE.get(o.service_id).name,
             o.region, o.public_url] for o in objects]


def list_endpoint_templates():
    objects = db_api.ENDPOINT_TEMPLATE.get_all()
    if objects == None:
        raise IndexError("URLs not found")
    return [[db_api.SERVICE.get(o.service_id).name,
             o.region, o.public_url] for o in objects]


def add_endpoint(tenant, endpoint_template):
    tenant = db_api.TENANT.get_by_name(name=tenant).id

    obj = db_models.Endpoints()
    obj.tenant_id = tenant
    obj.endpoint_template_id = endpoint_template
    db_api.ENDPOINT_TEMPLATE.endpoint_add(obj)
    return obj


def add_token(token, user, tenant, expires):
    user = db_api.USER.get_by_name(name=user).id
    tenant = db_api.TENANT.get_by_name(name=tenant).id

    obj = db_models.Token()
    obj.id = token
    obj.user_id = user
    obj.tenant_id = tenant
    obj.expires = datetime.datetime.strptime(expires.replace("-", ""),
        "%Y%m%dT%H:%M")
    return db_api.TOKEN.create(obj)


def list_tokens():
    objects = db_api.TOKEN.get_all()
    if objects == None:
        raise IndexError("Tokens not found")
    return [[o.id, o.user_id, o.expires, o.tenant_id] for o in objects]


def delete_token(token):
    obj = db_api.TOKEN.get(token)
    if obj == None:
        raise IndexError("Token %s not found" % (token,))
    return db_api.TOKEN.delete(token)


def add_service(name, type, desc):
    obj = db_models.Service()
    obj.name = name
    obj.type = type
    obj.desc = desc
    return db_api.SERVICE.create(obj)


def list_services():
    objects = db_api.SERVICE.get_all()
    if objects == None:
        raise IndexError("Services not found")
    return [[o.id, o.name, o.type] for o in objects]


def add_credentials(user, type, key, secrete, tenant=None):
    user = db_api.USER.get_by_name(user).id

    if tenant:
        tenant = db_api.TENANT.get_by_name(tenant).id

    obj = db_models.Token()
    obj.user_id = user
    obj.type = type
    obj.key = key
    obj.secret = secrete
    obj.tenant_id = tenant
    return db_api.CREDENTIALS.create(obj)
