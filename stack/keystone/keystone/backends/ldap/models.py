from collections import Mapping

__all__ = ['UserRoleAssociation', 'Endpoints', 'Role', 'Tenant', 'User',
           'Credentials']


def create_model(name, attrs):
    class C(Mapping):
        __slots__ = attrs

        def __init__(self, arg=None, **kwargs):
            if arg is None:
                arg = kwargs
            if isinstance(arg, dict):
                missed_attrs = set(attrs)
                for k, v in kwargs.iteritems():
                    setattr(self, k, v)
                    missed_attrs.remove(k)
                for name in missed_attrs:
                    setattr(self, name, None)
            elif isinstance(arg, C):
                for name in attrs:
                    setattr(self, name, getattr(arg, name))
            else:
                raise ValueError

        def __getitem__(self, name):
            return getattr(self, name)

        def __setitem__(self, name, value):
            return setattr(self, name, value)

        def __iter__(self):
            return iter(attrs)

        def __len__(self):
            return len(attrs)
    C.__name__ = name
    return C


UserRoleAssociation = create_model(
    'UserRoleAssociation', ['id', 'user_id', 'role_id', 'tenant_id'])
Endpoints = create_model(
    'Endpoints', ['tenant_id', 'endpoint_template_id'])
Role = create_model(
    'Role', ['id', 'desc', 'service_id'])
Tenant = create_model(
    'Tenant', ['id', 'desc', 'enabled'])
User = create_model(
    'User', ['id', 'password', 'email', 'enabled', 'tenant_id'])
Credentials = create_model(
    'Credentials', ['user_id', 'type', 'key', 'secret'])
