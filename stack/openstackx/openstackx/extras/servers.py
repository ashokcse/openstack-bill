import base64
from openstackx.api import base
from openstackx import compute


class Server(compute.Server):
    def __repr__(self):
        return "<Server>"

    def update(self, name=None, password=None, description=None):
        """
        Update the name or the password for this server.

        :param name: Update the server's name.
        :param password: Update the root password.
        :param description: Update the description
        """
        self.manager.update(self, name, password, description)


class ServerManager(compute.ServerManager):
    resource_class = Server

    def get(self, server_id):
        return self._get("/extras/servers/%s" % server_id, "server")

    def list(self):
        return self._list("/extras/servers", "servers")

    def update(self, server, name=None, password=None, description=None):
        """
        Update the name or the password for a server.

        :param server: The :class:`Server` (or its ID) to update.
        :param name: Update the server's name.
        :param password: Update the root password.
        """

        if name is None and password is None and description is None:
            return
        body = {"server": {}}
        if description:
            body["server"]["description"] = description
        if name:
            body["server"]["name"] = name
        if password:
            body["server"]["adminPass"] = password
        self._update("/extras/servers/%s" % base.getid(server), body)

    def create(self, name, image, flavor, ipgroup=None, meta=None, files=None, key_name=None, user_data=None, security_groups=None):
        """
        Create (boot) a new server.

        :param name: Something to name the server.
        :param image: The :class:`Image` to boot with.
        :param flavor: The :class:`Flavor` to boot onto.
        :param ipgroup: An initial :class:`IPGroup` for this server.
        :param key_name: Name of keypair that will be used for instance auth
        :param user_data: User supplied instance metadata
        :param meta: A dict of arbitrary key/value metadata to store for this
                     server. A maximum of five entries is allowed, and both
                     keys and values must be 255 characters or less.
        :param files: A dict of files to overrwrite on the server upon boot.
                      Keys are file names (i.e. ``/etc/passwd``) and values
                      are the file contents (either as a string or as a
                      file-like object). A maximum of five entries is allowed,
                      and each file must be 10k or less.

        There's a bunch more info about how a server boots in Rackspace's
        official API docs, page 23.
        """
        def get_href(link_list):
            for l in link_list:
                if l.get('type') == 'application/json':
                    return l['href']
                if l.get('rel') == 'self':
                    return l['href']
            return None

        # NOTE(vish): Split below is because compute is passing back a
        #             compute href but expects a glance href. Just passing
        #             the id (part after last /) uses the default glance.
        body = {"server": {
            "name": name,
            "imageRef": image['id'],
            "flavorRef": get_href(flavor.links),
        }}
        if ipgroup:
            body["server"]["sharedIpGroupId"] = base.getid(ipgroup)
        if meta:
            body["server"]["metadata"] = meta
        if user_data:
            body["server"]["user_data"] = base64.b64encode(user_data)
        if key_name:
            body["server"]["key_name"] = key_name
        if security_groups:
            body["server"]["security_groups"] = ','.join(security_groups)

        # Files are a slight bit tricky. They're passed in a "personality"
        # list to the POST. Each item is a dict giving a file name and the
        # base64-encoded contents of the file. We want to allow passing
        # either an open file *or* some contents as files here.
        if files:
            personality = body['server']['personality'] = []
            for filepath, file_or_string in files.items():
                if hasattr(file_or_string, 'read'):
                    data = file_or_string.read()
                else:
                    data = file_or_string
                personality.append({
                    'path': filepath,
                    'contents': data.encode('base64'),
                })

        return self._create("/extras/servers", body, "server")
