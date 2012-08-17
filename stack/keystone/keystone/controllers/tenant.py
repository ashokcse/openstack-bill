from keystone import utils
from keystone.common import wsgi
import keystone.config as config
from keystone.logic.types.tenant import Tenant
from . import get_marker_limit_and_url


class TenantController(wsgi.Controller):
    """Controller for Tenant related operations"""

    def __init__(self, options, is_service_operation=None):
        self.options = options
        self.is_service_operation = is_service_operation

    @utils.wrap_error
    def create_tenant(self, req):
        tenant = utils.get_normalized_request_content(Tenant, req)
        return utils.send_result(201, req,
            config.SERVICE.create_tenant(utils.get_auth_token(req), tenant))

    @utils.wrap_error
    def get_tenants(self, req):
        marker, limit, url = get_marker_limit_and_url(req)
        tenants = config.SERVICE.get_tenants(utils.get_auth_token(req),
            marker, limit, url, self.is_service_operation)
        return utils.send_result(200, req, tenants)

    @utils.wrap_error
    def get_tenant(self, req, tenant_id):
        tenant = config.SERVICE.get_tenant(utils.get_auth_token(req),
            tenant_id)
        return utils.send_result(200, req, tenant)

    @utils.wrap_error
    def update_tenant(self, req, tenant_id):
        tenant = utils.get_normalized_request_content(Tenant, req)
        rval = config.SERVICE.update_tenant(utils.get_auth_token(req),
            tenant_id, tenant)
        return utils.send_result(200, req, rval)

    @utils.wrap_error
    def delete_tenant(self, req, tenant_id):
        rval = config.SERVICE.delete_tenant(utils.get_auth_token(req),
            tenant_id)
        return utils.send_result(204, req, rval)
