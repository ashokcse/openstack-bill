__version__ = '2.0a1'

import os
import ConfigParser
from distutils.util import strtobool


DEFAULT_CONFIG_FILE = os.path.expanduser('~/.openstack/compute.conf')


class Config(object):

    """
    Encapsulates getting config from a number of places.

    Config passed in __init__ overrides config found in the environ, which
    finally overrides config found in a config file.
    """

    DEFAULTS = {
        'username': None,
        'apikey': None,
        'auth_token': None,
        'auth_url': "https://auth.api.rackspacecloud.com/v1.0",
        'management_url': None,
        'user_agent': 'python-openstack-compute/%s' % __version__,
        'allow_cache': False,
        'cloud_api': 'RACKSPACE',
    }

    def __init__(self, config_file, env, overrides,
                 env_prefix="OPENSTACK_COMPUTE_"):
        config_file = config_file or DEFAULT_CONFIG_FILE
        env = env or os.environ

        self.config = self.DEFAULTS.copy()
        self.update_config_from_file(config_file)
        self.update_config_from_env(env, env_prefix)
        self.config.update(dict((k, v) for (k, v) in overrides.items()
                                                   if v is not None))
        self.apply_fixups()

    def __getattr__(self, attr):
        try:
            return self.config[attr]
        except KeyError:
            raise AttributeError(attr)

    def update_config_from_file(self, config_file):
        """
        Update the config from a .ini file.
        """
        configparser = ConfigParser.RawConfigParser()
        if os.path.exists(config_file):
            configparser.read([config_file])

        # Mash together a bunch of sections -- "be liberal in what you accept."
        for section in ('global', 'compute', 'openstack.compute'):
            if configparser.has_section(section):
                self.config.update(dict(configparser.items(section)))

    def update_config_from_env(self, env, env_prefix):
        """
        Update the config from the environ.
        """
        for key, value in env.iteritems():
            if key.startswith(env_prefix):
                key = key.replace(env_prefix, '').lower()
                self.config[key] = value

    def apply_fixups(self):
        """
        Fix the types of any updates based on the original types in DEFAULTS.
        """
        for key, value in self.DEFAULTS.iteritems():
            if isinstance(value, bool)\
               and not isinstance(self.config[key], bool):
                self.config[key] = strtobool(self.config[key])
