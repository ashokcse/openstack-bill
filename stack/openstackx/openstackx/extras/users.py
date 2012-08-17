from openstackx.api import base


class User(base.Resource):
    def __repr__(self):
        return "<User %s>" % self._info

    def delete(self):
        self.manager.delete(self)


class UserManager(base.ManagerWithFind):
    resource_class = User

    def get(self, user_id):
        return self._get("/users/%s" % user_id, "user")

    def update_email(self, user_id, email):
        params = {"user": {"id": user_id,
                           "email": email }}

        self._update("/users/%s" % user_id, params)

    def update_enabled(self, user_id, enabled):
        params = {"user": {"id": user_id,
                           "enabled": enabled }}

        self._update("/users/%s/enabled" % user_id, params)

    def update_password(self, user_id, password):
        params = {"user": {"id": user_id,
                           "password": password }}

        self._update("/users/%s/password" % user_id, params)

    def update_tenant(self, user_id, tenant_id):
        params = {"user": {"id": user_id,
                           "tenantId": tenant_id }}

        self._update("/users/%s/tenant" % user_id, params)

    def create(self, name, email, password, tenant_id, enabled=True):
        params = {"user": {"name": name,
                           "email": email,
                           "tenantId": tenant_id,
                           "enabled": enabled,
                           "password": password}}
        return self._create('/users', params, "user")

    def delete(self, user_id):
        self._delete("/users/%s" % user_id)

    def list(self):
        """
        Get a list of users.
        :rtype: list of :class:`User`
        """
        return self._list("/users", "users")

    def get_for_tenant(self, tenant_id):
        return self._list("/tenants/%s/users" % tenant_id, "users")
