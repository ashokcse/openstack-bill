from openstackx.api import base


class Network(base.Resource):
    def __repr__(self):
        return "<Network: %s>" % self.name

    def delete(self):
        self.manager.delete(self)

    def update(self, *args, **kwargs):
        self.manager.update(self.name, *args, **kwargs)


class NetworkManager(base.ManagerWithFind):
    resource_class = Network

    def list(self, project_id=None):
        if project_id:
            return self._list("/admin/networks?tenant_id=%s" % project_id, "networks")
        else:
            return self._list("/admin/networks", "networks")

    def get(self, network_id):
        return self._get("/admin/networks/%s" % network_id, "network")

    def disassociate(self, network_id):
        self._delete("/admin/networks/%s/disassociate" % network_id)

    def create(self, name, *args, **kwargs):
        raise NotImplementedError()

    def delete(self, network_id):
        raise NotImplementedError()

    def update(self, name, *args, **kwargs):
        raise NotImplementedError()
