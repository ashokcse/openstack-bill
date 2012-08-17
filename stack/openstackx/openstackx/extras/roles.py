from openstackx.api import base


class Role(base.Resource):
    pass


class RoleManager(base.ManagerWithFind):
    resource_class = Role

    def list(self):
        return self._list("/OS-KSADM/roles", "roles")
