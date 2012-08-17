from openstackx.api import base


class RoleRef(base.Resource):
    def __getattr__(self, k):
        if k == "tenantId":
            setattr(self, k, None)
            return self.__dict__[k]
        return super(RoleRef, self).__getattr__(k)


class RoleRefManager(base.ManagerWithFind):
    resource_class = RoleRef

    def list_for_user(self, user_id):
        return self._list("/users/%s/roleRefs" % user_id, "roles")

    def add_for_tenant_user(self, tenant_id, user_id, role_id):
        params = {"role": {"tenantId": tenant_id, "roleId": role_id}}
        return self._create("/users/%s/roleRefs" % user_id, params, "role")

    def delete_for_tenant_user(self, tenant_id, user_id, role_id):
        role_refs = self.list_for_user(user_id)
        for role_ref in role_refs:
            if role_ref.roleId == role_id and tenant_id == role_ref.tenantId:
                return self._delete("/users/%s/roleRefs/%s" % (user_id, role_ref.id))
