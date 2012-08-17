import logging
from openstackx.api import base

LOG = logging.getLogger('openstackx.openstackx')

class Biller(base.Resource):
    def __repr__(self):
        return "<Biller %s>" % self._info

class BillerManager(base.ManagerWithFind):
    resource_class = Biller

    def get(self, biller_id):
	LOG.info("openstackx extra biller BillerManager get %d",biller_id)
        return self._get("/billers/%s" % biller_id, "biller")

    def create(self, vcpu, ram, vdisk, date, enabled=True):
        params = {"biller": {"vcpu": vcpu,
                           "ram": ram,
                           "vdisk": vdisk,
                           "date": date.strftime('%Y %m %d')
                           "enabled": enabled}}
        return self._create('/billers/create', params, "biller")  




