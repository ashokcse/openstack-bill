from openstackx.api import base
import os


class Endpoint(base.Resource):
    def __getattr__(self, k):
        if k == "endpointTemplateId":
            setattr(self, k, os.path.basename(self.href))
            return self.__dict__[k]
        return super(Endpoint, self).__getattr__(k)


class EndpointManager(base.ManagerWithFind):
    resource_class = Endpoint

    def list_for_tenant(self, tenant_id):
        return self._list("/tenants/%s/endpoints" % tenant_id, "endpoints")

    def add_for_tenant(self, tenant_id, endpoint_template_id):
        params = {"endpointTemplate": {"id": endpoint_template_id}}
        return self._create("/tenants/%s/endpoints" % tenant_id, params, "endpoint")

    def delete_for_tenant(self, tenant_id, endpoint_template_id):
        for endpoint in self.list_for_tenant(tenant_id):
            if endpoint.endpointTemplateId == endpoint_template_id:
                self._delete("/tenants/%s/endpoints/%s" % (tenant_id, endpoint.id))
                return
