import logging
import time
from  datetime import datetime
from openstackx.api import base

LOG = logging.getLogger('openstackx.openstackx')

class Biller(base.Resource):
    def __repr__(self):
        return "<Biller %s>" % self._info

class BillerManager(base.ManagerWithFind):
    resource_class = Biller

    def get(self, biller_date):
	LOG.info("openstackx extra biller BillerManager get %s" % biller_date)
        return self._get("/billers/%s" % biller_date, "biller")

    def create(self, vcpu, ram, vdisk, date, changed_on, enabled=True):
        params = {"biller": {"vcpu": vcpu,
                           "ram": ram,
                           "vdisk": vdisk,
                           "date": date,
                           "changed_on":changed_on,
                           "enabled": enabled}}
	LOG.info("openstackx extra biller BillerManager CREATE %s" % params)
        return self._create('/billers/create', params, "biller")  



    def get_ibill(self, instance_name):
        LOG.info("openstackx extra biller BillerManager get instance id :%s" % instance_name)
        return self._get("/billers/%s/instance" % instance_name, "biller")

    def create_ibill(self, id,  name, total_vcpu,  total_ram,  total_vdisk,  total_cost, changed_on, enabled=True):
        params = {"biller": {"id": id,
                           "name":  name,
                           "total_vcpu":  total_vcpu,
                           "total_ram":  total_ram,
                           "total_vdisk":  total_vdisk,
                           "total_cost": total_cost,
                           "changed_on":changed_on,
                           "enabled": enabled}}
        LOG.info("openstackx extra biller BillerManager CREATE Ibill %s" % params)
        return self._create('/billers/', params, "biller")

    def get_ubill(self, user_id, bill_month):
        LOG.info("openstackx extra biller BillerManager get user id :%s   bill month :%s" % (user_id,bill_month))
        return self._get("/billers/%s/user_bill/%s" % (user_id, bill_month), "biller")

    def create_ubill(self, id,  user_id, tenant_id, total_vcpu,  total_ram,  total_vdisk,  total_cost, bill_month, enabled):
        params = {"biller": {"id": id,
                           "user_id": user_id,
                           "tenant_id": tenant_id,
                           "total_vcpu":  total_vcpu,
                           "total_ram":  total_ram,
                           "total_vdisk":  total_vdisk,
                           "total_cost": total_cost,
                           "bill_month": bill_month,
                           "enabled": enabled}}
        LOG.info("openstackx extra biller BillerManager CREATE Ubill %s" % params)
        return self._create('/billers/user_bill', params, "biller")

