from openstackx.api import base


class Usage(base.Resource):
    def __repr__(self):
        return "<ComputeUsage>"

class UsageManager(base.ManagerWithFind):
    resource_class = Usage

    def list(self, start, end):
        return self._list("/extras/usage?start=%s&end=%s" % (start.isoformat(), end.isoformat()), "usage")

    def get(self, tenant_id, start, end):
        return self._get("/extras/usage/%s?start=%s&end=%s" % (tenant_id, start.isoformat(), end.isoformat()), "usage")
