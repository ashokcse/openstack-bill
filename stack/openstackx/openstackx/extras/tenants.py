from openstackx.api import base


class Tenant(base.Resource):
    def __repr__(self):
        return "<Tenant %s>" % self._info

    def delete(self):
        self.manager.delete(self)

    def update(self, description=None, enabled=None):
        self.manager.update(self.id, description, enabled)


class TenantManager(base.ManagerWithFind):
    resource_class = Tenant

    def get(self, tenant_id):
        return self._get("/tenants/%s" % tenant_id, "tenant")

#    def get_user_role_refs(self, user_id):
#        return self._get("/users/%s/roleRefs" % user_id, "roleRefs")

#    def add_tenant_user(self, tenant_id, user_id):
#        params = {"roleRef": {"tenantId": tenant_id, "roleId": "Member"}}
#        return self._create("/users/%s/roleRefs" % user_id, params, "roleRef")
#
#    def remove_tenant_user(self, tenant_id, user_id):
#        params = {}
#        return self._delete("/users/%s/roleRefs/5" % user_id)

    def create(self, name, description, enabled=True):
        params = {"tenant": {"name":name,
                             "description": description,
                             "enabled": enabled}}

        return self._create('/tenants', params, "tenant")

    def list(self):
        """
        Get a list of tenants.
        :rtype: list of :class:`Tenant`
        """
        return self._list("/tenants", "tenants")

    def update(self, tenant_id, tenant_name=None, description=None, enabled=None):
        """
        update a tenant with a new name and description
        """
        body = {"tenant": {'id': tenant_id}}
        if tenant_name is not None:
            body['tenant']['name'] = tenant_name
        if enabled is not None:
            body['tenant']['enabled'] = enabled
        if description:
            body['tenant']['description'] = description

        self._update("/tenants/%s" % tenant_id, body)

    def delete(self, tenant_id):
        """
        Delete a tenant
        """
        self._delete("/tenants/%s" % tenant_id)
