from openstackx.api import base


class VirtualInterfaces(base.Resource):
    def __repr__(self):
        return "<VirtualInterface>"


class VirtualInterfacesManager(base.ManagerWithFind):
    resource_class = VirtualInterfaces

    def list(self, instance_id):
        return self._list('/servers/%s/os-virtual-interfaces' % instance_id, 'virtual_interfaces')
