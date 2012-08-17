from openstackx.api import base


class SecurityGroupRule(base.Resource):
    pass


class SecurityGroupRuleManager(base.ManagerWithFind):
    resource_class = SecurityGroupRule

    def create(self, parent_group_id, ip_protocol=None, from_port=None, to_port=None, cidr=None, group_id=None):
        body = { "security_group_rule": { "ip_protocol": ip_protocol,
                           "from_port": from_port,
                           "to_port": to_port,
                           "cidr": cidr,
                           "group_id": group_id,
                           "parent_group_id": parent_group_id }}

        return self._create('/extras/security_group_rules', body, "security_group_rule")

    def delete(self, id):
        return self._delete('/extras/security_group_rules/%s' % id)
