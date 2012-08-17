__version__ = '2.0a1'

import os
from distutils.util import strtobool
from openstackx.api.connection import ApiConnection
from openstackx.api.config import Config
from openstackx.compute.backup_schedules import (BackupSchedule, BackupScheduleManager,
        BACKUP_WEEKLY_DISABLED, BACKUP_WEEKLY_SUNDAY, BACKUP_WEEKLY_MONDAY,
        BACKUP_WEEKLY_TUESDAY, BACKUP_WEEKLY_WEDNESDAY,
        BACKUP_WEEKLY_THURSDAY, BACKUP_WEEKLY_FRIDAY, BACKUP_WEEKLY_SATURDAY,
        BACKUP_DAILY_DISABLED, BACKUP_DAILY_H_0000_0200,
        BACKUP_DAILY_H_0200_0400, BACKUP_DAILY_H_0400_0600,
        BACKUP_DAILY_H_0600_0800, BACKUP_DAILY_H_0800_1000,
        BACKUP_DAILY_H_1000_1200, BACKUP_DAILY_H_1200_1400,
        BACKUP_DAILY_H_1400_1600, BACKUP_DAILY_H_1600_1800,
        BACKUP_DAILY_H_1800_2000, BACKUP_DAILY_H_2000_2200,
        BACKUP_DAILY_H_2200_0000)
from openstackx.compute.exceptions import (ComputeException, BadRequest, Unauthorized,
    Forbidden, NotFound, OverLimit)
from openstackx.compute.flavors import FlavorManager, Flavor
from openstackx.compute.images import ImageManager, Image
from openstackx.compute.ipgroups import IPGroupManager, IPGroup
from openstackx.compute.servers import ServerManager, Server, REBOOT_HARD, REBOOT_SOFT
from openstackx.compute.api import API_OPTIONS

DEFAULT_CONFIG_FILE = os.path.expanduser('~/.openstack/compute.conf')

class Compute(object):
    """
    Top-level object to access the OpenStack Compute API.

    Create an instance with your creds::

    >>> compute = Compute(username=USERNAME, apikey=API_KEY)

    Then call methods on its managers::

        >>> compute.servers.list()
        ...
        >>> compute.flavors.list()
        ...

    &c.
    """

    def __init__(self, **kwargs):
        self.config = self._get_config(kwargs)
        self.backup_schedules = BackupScheduleManager(self)
        self.connection = ApiConnection(self.config)
        self.flavors = FlavorManager(self)
        self.images = ImageManager(self)
        self.servers = ServerManager(self)
        if 'IPGROUPS' in API_OPTIONS[self.config.cloud_api]:
            self.ipgroups = IPGroupManager(self)

    def authenticate(self):
        """
        Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`~openstack.compute.Unauthorized` if
        the credentials are wrong.
        """
        pass
        #self.connection.authenticate()

    def _get_config(self, kwargs):
        """
        Get a Config object for this API client.

        Broken out into a seperate method so that the test client can easily
        mock it up.
        """
        return Config(
            config_file = kwargs.pop('config_file', None),
            env = kwargs.pop('env', None),
            overrides = kwargs,
        )
