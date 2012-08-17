from openstackx.api import base


class Server(base.Resource):
    def __repr__(self):
        return "<Server>"


class ServerManager(base.ManagerWithFind):
    resource_class = Server

    def get(self, server_id):
        return self._get("/admin/servers/%s" % server_id, "server")

    def list(self):
        return self._list("/admin/servers", "servers")

