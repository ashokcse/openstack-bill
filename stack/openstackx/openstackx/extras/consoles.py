from openstackx.api import base


class Console(base.Resource):
    def __repr__(self):
        return "<Console>"


class ConsoleManager(base.ManagerWithFind):
    resource_class = Console

    def create(self, server_id, console_type='text'):
        body = {"console": {"type": console_type, 'server_id': server_id}}
        return self._create('/extras/consoles', body, "console")
