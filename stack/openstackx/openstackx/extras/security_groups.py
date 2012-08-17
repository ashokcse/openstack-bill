from openstackx.api import base


class SecurityGroup(base.Resource):
    pass


class SecurityGroupManager(base.ManagerWithFind):
    resource_class = SecurityGroup

    def list(self):
        """
        Get a list of all security_groups.
        
        :rtype: list of :class:`SecurityGroup`.
        """
        return self._list("/extras/security_groups", "security_groups")

    def create(self, name, description):
        body = {"security_group": {"name": name, 'description': description}}
        return self._create('/extras/security_groups', body, 'security_group')

    def delete(self, id):
        return self._delete('/extras/security_groups/%s' % id)

    def get(self, id):
        return self._get('/extras/security_groups/%s' % id, 'security_group')
