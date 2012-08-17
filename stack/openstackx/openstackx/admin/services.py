from openstackx.api import base
from openstackx.compute.api import API_OPTIONS


class Services(base.Resource):
    def update(self, disabled):
        self.manager.update(self.id, disabled)


class ServiceManager(base.ManagerWithFind):
    resource_class = Services

    def list(self):
        return self._list("/admin/services", "services")

    def get(self, id):
        return self._get("/admin/services/%s" % id, "service")

    def update(self, id, disabled):
        body = {"service": {'disabled': disabled}}
        self._update("/admin/services/%s" % id, body)
