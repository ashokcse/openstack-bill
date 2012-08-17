from openstackx.api import base


class Tenant(base.Resource):
    def __repr__(self):
        return "<Tenant %s>" % self._info

    @property
    def id(self):
        return self._info['id']

    @property
    def description(self):
        return self._info['description']

    @property
    def enabled(self):
        return self._info['enabled']


class Token(base.Resource):
    def __repr__(self):
        return "<Token %s>" % self._info

    @property
    def id(self):
        return self._info['token']['id']

    @property
    def username(self):
        try:
            return self._info['user']['username'] 
        except:
            return "?"

    @property
    def tenant_id(self):
        try:
            return self._info['user']['tenantId'] 
        except:
            return "?"

    def delete(self):
        self.manager.delete(self)


class TokenManager(base.ManagerWithFind):
    resource_class = Token

    def create(self, tenant, username, password):
        params = {"auth": {"passwordCredentials": {"username": username,
                                          "password": password},
                                          "tenantId": tenant}}

        return self._create('tokens', params, "access")

    def create_scoped_with_token(self, tenant, token):
        params = {"auth": {"tenantId": tenant, "token": {"id": token}}}
        return self._create('tokens', params, "access")


class TenantManager(base.ManagerWithFind):
    resource_class = Tenant

    def for_token(self, token):
        # FIXME(ja): now that tenants & tokens are separate managers we shouldn't
        # need the uglyness of setting token this way?
        orig = self.api.connection.auth_token
        self.api.connection.auth_token = token
        rval = self._list('tenants', "tenants")
        self.api.connection.auth_token = orig
        return rval

