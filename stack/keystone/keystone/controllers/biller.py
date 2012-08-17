import logging
from keystone import utils
from keystone.common import wsgi
import keystone.config as config
from keystone.logic.types.biller import Bill_Unit, Instance_Bill, User_Bill
from . import get_marker_limit_and_url


LOG = logging.getLogger('keystone.logic.service')

class BillController(wsgi.Controller):
    """Controller for User related operations"""

    def __init__(self, options):
        self.options = options

    """@utils.wrap_error
    def create_user(self, req):
        u = utils.get_normalized_request_content(User, req)
        return utils.send_result(201, req, config.SERVICE.create_user(
            utils.get_auth_token(req), u))

    @utils.wrap_error
    def get_users(self, req):
        marker, limit, url = get_marker_limit_and_url(req)
        users = config.SERVICE.get_users(utils.get_auth_token(req), marker,
            limit, url)
        return utils.send_result(200, req, users)"""

    @utils.wrap_error
    def get_billunit(self, req, biller_date):
        billunit = config.SERVICE.get_bill_unit(biller_date)
        LOG.info('keystone controller biller py get_billunit billunit id:%d vcpu:%d ram:%d vdisk: %d date: %s changed_on: %s enabled:%d'% (billunit.id, billunit.vcpu, billunit.ram, billunit.vdisk, billunit.date, billunit.changed_on, billunit.enabled))
        return utils.send_result(200, req, billunit)
        
    @utils.wrap_error
    def create_billunit(self, req):
	LOG.info('Before get_normalization Creating creat_billunit (self, req,) controller.biller.py')
        u = utils.get_normalized_request_content(Bill_Unit, req)
	LOG.info('Creating creat_billunit (self, req,) controller.biller.py :date: %s |enable:%s cpu:%s'%(u.date,u.enabled,u.vcpu))
        return utils.send_result(201, req, config.SERVICE.create_bill_unit(utils.get_auth_token(req), u))

    @utils.wrap_error
    def get_instance_bill(self, req, instance_id):
        LOG.info('keystone Before controller biller py get_instance bill ')
        instance = config.SERVICE.get_instance_bill(instance_id)
        LOG.info('keystone controller biller py get_instance bill ')
        return utils.send_result(200, req, instance)

    @utils.wrap_error
    def create_instance_bill(self, req):
        LOG.info('Before get_normalization Creating creat_instance_bill (self, req,) controller.biller.py')
        u = utils.get_normalized_request_content(Instance_Bill, req)
        LOG.info('Creating creat_instacne (self, req,) controller.biller.py id :%s : name: %s |enable:%s cpu:%s'%(u.id,u.name,u.enabled,u.total_vcpu))
        return utils.send_result(201, req, config.SERVICE.create_instance_bill(utils.get_auth_token(req), u))


    @utils.wrap_error
    def get_user_bill(self, req, user_id, month):
        LOG.info('keystone Before controller biller py get_userbill ')
        userbill = config.SERVICE.get_user_bill(user_id,month)
        LOG.info('keystone controller biller py get_user bill ')
        return utils.send_result(200, req, userbill)

    @utils.wrap_error
    def create_user_bill(self, req):
        LOG.info('Before get_normalization Creating creat_instance_bill (self, req,) controller.biller.py')
        u = utils.get_normalized_request_content(User_Bill, req)
        LOG.info('Creating creat_instacne (self, req,) controller.biller.py id :%s : name: %s |enable:%s cpu:%s'%(u.id,u.tenant_id,u.enabled,u.total_vcpu))
        return utils.send_result(201, req, config.SERVICE.create_user_bill(utils.get_auth_token(req), u))
                
